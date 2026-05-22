"""Service Quota — Firestore transactions atomiques.

Collection Firestore : `user_quotas/{user_id}` =
  {
    remaining_scans: int,
    plan: str,
    expires_at: timestamp,
    last_scan_at: timestamp,
    scans_this_hour: int,
    hour_window_start: timestamp,
    family_id: str | null,
  }

Cf. docs/architecture.md + docs/pricing.md mécanismes anti-abus.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import structlog
from google.cloud import firestore

from app.core.config import settings
from app.db.firestore import get_firestore_client

logger = structlog.get_logger(__name__)


class QuotaError(Exception):
    """Erreur métier quota."""


class QuotaExhaustedError(QuotaError):
    """Plus de scans disponibles."""


class QuotaThrottledError(QuotaError):
    """Trop de scans dans la fenêtre horaire."""


class QuotaExpiredError(QuotaError):
    """Crédit expiré (compte en grace ou frozen)."""


@dataclass(frozen=True)
class QuotaStatus:
    """Vue d'un quota utilisateur."""

    remaining_scans: int
    plan: str
    expires_at: datetime | None
    days_until_expiry: int | None
    scans_this_hour: int
    is_active: bool


class QuotaService:
    """Gère le quota côté Firestore avec transactions atomiques."""

    def __init__(self) -> None:
        self.client = get_firestore_client()

    # ──────────────────────────────────────────────
    #  Granting credits (paiement OK)
    # ──────────────────────────────────────────────
    async def grant_credits(
        self,
        user_id: uuid.UUID,
        plan: str,
        scans: int,
        duration_days: int,
        family_id: uuid.UUID | None = None,
    ) -> QuotaStatus:
        """Accorde des crédits à un utilisateur (rotation = nouveau plan remplace l'ancien)."""
        now = datetime.now(UTC)
        expires_at = now + timedelta(days=duration_days)

        ref = self.client.collection("user_quotas").document(str(user_id))
        data = {
            "remaining_scans": scans,
            "plan": plan,
            "expires_at": expires_at,
            "granted_at": now,
            "scans_granted_total": scans,
            "family_id": str(family_id) if family_id else None,
            "scans_this_hour": 0,
            "hour_window_start": now,
        }
        await ref.set(data, merge=False)                       # remplace l'ancien quota

        logger.info(
            "quota.granted",
            user_id=str(user_id),
            plan=plan,
            scans=scans,
            duration_days=duration_days,
        )
        return QuotaStatus(
            remaining_scans=scans,
            plan=plan,
            expires_at=expires_at,
            days_until_expiry=duration_days,
            scans_this_hour=0,
            is_active=True,
        )

    # ──────────────────────────────────────────────
    #  Pre-flight check (avant ouverture caméra)
    # ──────────────────────────────────────────────
    async def check(self, user_id: uuid.UUID) -> QuotaStatus:
        """Pre-flight quota check — appelé AVANT toute opération de scan.

        Ne décrémente PAS. N'incrémente PAS le throttle.
        """
        ref = self.client.collection("user_quotas").document(str(user_id))
        snap = await ref.get()
        if not snap.exists:
            return QuotaStatus(
                remaining_scans=0,
                plan="none",
                expires_at=None,
                days_until_expiry=None,
                scans_this_hour=0,
                is_active=False,
            )

        d = snap.to_dict() or {}
        expires_at = d.get("expires_at")
        now = datetime.now(UTC)

        # Expiration ?
        if expires_at and expires_at < now:
            days_until = -((now - expires_at).days)
            return QuotaStatus(
                remaining_scans=0,
                plan=d.get("plan", "none"),
                expires_at=expires_at,
                days_until_expiry=days_until,
                scans_this_hour=d.get("scans_this_hour", 0),
                is_active=False,
            )

        days_until = (expires_at - now).days if expires_at else None
        return QuotaStatus(
            remaining_scans=d.get("remaining_scans", 0),
            plan=d.get("plan", "none"),
            expires_at=expires_at,
            days_until_expiry=days_until,
            scans_this_hour=d.get("scans_this_hour", 0),
            is_active=True,
        )

    # ──────────────────────────────────────────────
    #  Consume scan (transaction atomique)
    # ──────────────────────────────────────────────
    async def consume_scan(self, user_id: uuid.UUID) -> int:
        """Décrémente atomiquement le quota. Throttle aussi en même temps.

        Returns:
            remaining_scans après décrément.

        Raises:
            QuotaExhaustedError : 0 restants
            QuotaThrottledError : > 20 scans dans l'heure
            QuotaExpiredError : crédit expiré
        """
        ref = self.client.collection("user_quotas").document(str(user_id))

        @firestore.async_transactional
        async def _transaction(transaction: firestore.AsyncTransaction, ref: firestore.AsyncDocumentReference) -> int:
            snap = await ref.get(transaction=transaction)
            if not snap.exists:
                raise QuotaExhaustedError("Aucun crédit. Achetez un ticket pour commencer.")

            d = snap.to_dict() or {}
            now = datetime.now(UTC)

            # Expiration
            expires_at = d.get("expires_at")
            if expires_at and expires_at < now:
                raise QuotaExpiredError("Crédit expiré. Renouvelez votre abonnement.")

            # Throttle (fenêtre glissante 1h)
            hour_start = d.get("hour_window_start") or now
            scans_this_hour = d.get("scans_this_hour", 0)
            if (now - hour_start) > timedelta(hours=1):
                scans_this_hour = 0
                hour_start = now
            if scans_this_hour >= settings.quota_throttle_scans_per_hour:
                raise QuotaThrottledError(
                    f"Trop de scans cette heure ({scans_this_hour}). Réessayez plus tard."
                )

            remaining = d.get("remaining_scans", 0)
            if remaining <= 0:
                raise QuotaExhaustedError("Crédit épuisé. Achetez un ticket pour continuer.")

            new_remaining = remaining - 1
            transaction.update(
                ref,
                {
                    "remaining_scans": new_remaining,
                    "scans_this_hour": scans_this_hour + 1,
                    "hour_window_start": hour_start,
                    "last_scan_at": now,
                },
            )
            return new_remaining

        transaction = self.client.transaction()
        remaining = await _transaction(transaction, ref)

        logger.info(
            "quota.consumed",
            user_id=str(user_id),
            remaining_after=remaining,
        )
        return remaining

    # ──────────────────────────────────────────────
    #  Refund (en cas d'erreur OCR par exemple)
    # ──────────────────────────────────────────────
    async def refund_scan(self, user_id: uuid.UUID, reason: str) -> int:
        """Rembourse un scan en cas d'erreur backend (OCR fail, etc.)."""
        ref = self.client.collection("user_quotas").document(str(user_id))

        @firestore.async_transactional
        async def _transaction(transaction: firestore.AsyncTransaction, ref: firestore.AsyncDocumentReference) -> int:
            snap = await ref.get(transaction=transaction)
            if not snap.exists:
                return 0
            d = snap.to_dict() or {}
            remaining = d.get("remaining_scans", 0) + 1
            transaction.update(ref, {"remaining_scans": remaining})
            return remaining

        transaction = self.client.transaction()
        remaining = await _transaction(transaction, ref)

        logger.info("quota.refunded", user_id=str(user_id), reason=reason, remaining=remaining)
        return remaining
