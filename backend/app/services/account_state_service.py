"""Service AccountState — gère les transitions du cycle de vie compte.

Cycle (cf. docs/strategie_Nasoma.md § 3 quater) :
  ACTIVE → GRACE (crédit expiré, 30j lecture seule)
         → FROZEN (J+31 à J+365, pas d'accès direct)
         → ARCHIVED (> J+365, anonymisation par défaut à J+395)

Transitions :
  - Triggered automatically par cron quotidien
  - Triggered au login : si state stale, recalculer en live
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.users import AccountState, User

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class AccountStateInfo:
    """État compte enrichi pour les réponses API."""

    state: AccountState
    credit_expires_at: datetime | None
    days_remaining_grace: int | None
    days_until_freeze: int | None
    days_since_freeze: int | None
    can_login_direct: bool
    can_perform_new_actions: bool
    can_read_data: bool
    paywall_required: bool


class AccountStateService:
    """Gère les transitions et le calcul de l'état d'un compte."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_info(self, user_id: uuid.UUID) -> AccountStateInfo:
        """Retourne l'état enrichi d'un compte (recalcule en live au besoin)."""
        user = await self.db.get(User, user_id)
        if user is None:
            raise ValueError(f"User {user_id} not found")

        # Recalculer l'état si nécessaire (cron pas encore passé)
        computed_state = self._compute_state(user)
        if computed_state != user.account_state:
            await self._transition(user, computed_state)

        return self._build_info(user)

    async def transition_all_due(self) -> dict[str, int]:
        """Cron quotidien : applique toutes les transitions dues.

        Returns:
            { "active_to_grace": N, "grace_to_frozen": N, "frozen_to_archived": N }
        """
        now = datetime.now(UTC)
        counts: dict[str, int] = {
            "active_to_grace": 0,
            "grace_to_frozen": 0,
            "frozen_to_archived": 0,
        }

        # ACTIVE → GRACE (credit_expires_at < NOW)
        stmt_grace = (
            update(User)
            .where(
                User.account_state == AccountState.ACTIVE,
                User.credit_expires_at.isnot(None),
                User.credit_expires_at < now,
            )
            .values(account_state=AccountState.GRACE, state_changed_at=now)
        )
        res = await self.db.execute(stmt_grace)
        counts["active_to_grace"] = res.rowcount or 0

        # GRACE → FROZEN (credit_expires_at + grace_days < NOW)
        grace_cutoff = now - timedelta(days=settings.quota_grace_period_days)
        stmt_frozen = (
            update(User)
            .where(
                User.account_state == AccountState.GRACE,
                User.credit_expires_at < grace_cutoff,
            )
            .values(
                account_state=AccountState.FROZEN,
                state_changed_at=now,
                last_valid_otp_hash=None,                      # invalidation OTP au gel
                last_valid_otp_expires_at=None,
            )
        )
        res = await self.db.execute(stmt_frozen)
        counts["grace_to_frozen"] = res.rowcount or 0

        # FROZEN → ARCHIVED (credit_expires_at + 365j < NOW)
        archived_cutoff = now - timedelta(days=settings.quota_frozen_to_archived_days)
        stmt_archived = (
            update(User)
            .where(
                User.account_state == AccountState.FROZEN,
                User.credit_expires_at < archived_cutoff,
            )
            .values(account_state=AccountState.ARCHIVED, state_changed_at=now)
        )
        res = await self.db.execute(stmt_archived)
        counts["frozen_to_archived"] = res.rowcount or 0

        await self.db.commit()
        logger.info("account_state.cron_transitions", **counts)
        return counts

    # ──────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────
    def _compute_state(self, user: User) -> AccountState:
        """Calcule l'état réel d'un user à partir de credit_expires_at."""
        if user.credit_expires_at is None:
            return user.account_state

        now = datetime.now(UTC)
        expires = user.credit_expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)

        if expires > now:
            return AccountState.ACTIVE

        days_since_expiry = (now - expires).days
        if days_since_expiry < settings.quota_grace_period_days:
            return AccountState.GRACE
        if days_since_expiry < settings.quota_frozen_to_archived_days:
            return AccountState.FROZEN
        return AccountState.ARCHIVED

    async def _transition(self, user: User, new_state: AccountState) -> None:
        """Force la transition d'un user et persiste."""
        old_state = user.account_state
        user.account_state = new_state
        user.state_changed_at = datetime.now(UTC)
        if new_state == AccountState.FROZEN:
            user.last_valid_otp_hash = None
            user.last_valid_otp_expires_at = None
        await self.db.flush()

        logger.info(
            "account_state.transition",
            user_id=str(user.id),
            from_state=old_state,
            to_state=new_state,
        )

    def _build_info(self, user: User) -> AccountStateInfo:
        now = datetime.now(UTC)
        expires = user.credit_expires_at
        if expires and expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)

        days_remaining_grace: int | None = None
        days_until_freeze: int | None = None
        days_since_freeze: int | None = None

        if user.account_state == AccountState.GRACE and expires:
            days_since_expiry = (now - expires).days
            days_remaining_grace = max(
                0, settings.quota_grace_period_days - days_since_expiry
            )
        if user.account_state == AccountState.ACTIVE and expires:
            days_until_freeze = (expires - now).days + settings.quota_grace_period_days
        if user.account_state == AccountState.FROZEN and expires:
            days_since_freeze = (
                (now - expires).days - settings.quota_grace_period_days
            )

        state = user.account_state
        return AccountStateInfo(
            state=state,
            credit_expires_at=expires,
            days_remaining_grace=days_remaining_grace,
            days_until_freeze=days_until_freeze,
            days_since_freeze=days_since_freeze,
            can_login_direct=state in (AccountState.ACTIVE, AccountState.GRACE),
            can_perform_new_actions=state == AccountState.ACTIVE,
            can_read_data=state in (AccountState.ACTIVE, AccountState.GRACE),
            paywall_required=state != AccountState.ACTIVE,
        )

    @staticmethod
    def access_mode_for(state: AccountState) -> Literal["full", "readonly", "denied"]:
        """Helper UI : mode d'accès pour un état donné."""
        if state == AccountState.ACTIVE:
            return "full"
        if state == AccountState.GRACE:
            return "readonly"
        return "denied"
