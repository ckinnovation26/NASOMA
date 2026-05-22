"""Service Billing — gestion des outstanding bills + session vidéo + dashboard vendeur.

Workflow :
1. User en compte ACTIVE demande assistance vidéo → disclosure obligatoire
2. User consent → session démarre
3. À la fin → calcul durée + création OutstandingBill
4. À la prochaine recharge, vendeur voit la dette et la propose au règlement
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.billing import (
    BillKind,
    BillStatus,
    OutstandingBill,
    VideoAssistanceSession,
    VideoAssistanceStatus,
)
from app.models.users import AccountState, User

logger = structlog.get_logger(__name__)


class BillingError(Exception):
    """Erreur métier billing."""


class AccountNotActiveError(BillingError):
    """Compte non-actif — service refusé."""


@dataclass(frozen=True)
class CustomerDashboard:
    """Snapshot client pour vendeur — affiché dès saisie du numéro."""

    user_id: uuid.UUID
    phone: str
    account_state: str
    full_name: str | None
    outstanding_bills: list[OutstandingBill]
    total_due_kmf: int
    eligible_for_video_assistance: bool          # True si ACTIVE


class BillingService:
    """Outstanding bills + video assistance + vendor dashboard."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ──────────────────────────────────────────────
    #  Video assistance — création disclosure
    # ──────────────────────────────────────────────
    async def request_video_assistance(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> VideoAssistanceSession:
        """Crée une demande d'assistance vidéo. Vérifie account_state == ACTIVE.

        Retourne la session avec disclosure_text à présenter au user.
        Le user doit ensuite confirmer via `confirm_disclosure(session_id)`.
        """
        user = await self.db.get(User, user_id)
        if user is None:
            raise BillingError("User not found")

        state_str = (
            user.account_state.value
            if hasattr(user.account_state, "value")
            else str(user.account_state)
        )

        # Service réservé aux comptes ACTIVE (décision business)
        if user.account_state != AccountState.ACTIVE:
            session = VideoAssistanceSession(
                tenant_id=tenant_id,
                user_id=user_id,
                account_state_at_request=state_str,
                status=VideoAssistanceStatus.REFUSED_NOT_ACTIVE,
                rate_kmf_per_10min=settings.video_assistance_rate_kmf_per_10min,
                user_consent=False,
            )
            self.db.add(session)
            await self.db.flush()
            logger.info(
                "video.refused_not_active",
                user_id=str(user_id),
                state=state_str,
            )
            raise AccountNotActiveError(
                "L'assistance vidéo est réservée aux abonnés actifs. "
                "Réactivez votre abonnement chez un vendeur pour y accéder."
            )

        # Concaténer free alternative + paid disclosure pour audit complet
        full_disclosure = (
            f"{settings.video_assistance_free_alternative_text}\n\n"
            f"{settings.video_assistance_disclosure_text}"
        )
        session = VideoAssistanceSession(
            tenant_id=tenant_id,
            user_id=user_id,
            account_state_at_request=state_str,
            status=VideoAssistanceStatus.REQUESTED,
            rate_kmf_per_10min=settings.video_assistance_rate_kmf_per_10min,
            disclosure_text=full_disclosure,
            user_consent=False,
        )
        self.db.add(session)
        await self.db.flush()
        logger.info(
            "video.requested",
            user_id=str(user_id),
            session_id=str(session.id),
        )
        return session

    async def confirm_disclosure(
        self, session_id: uuid.UUID, user_id: uuid.UUID
    ) -> VideoAssistanceSession:
        """L'utilisateur confirme la tarification — passage en DISCLOSED."""
        session = await self.db.get(VideoAssistanceSession, session_id)
        if session is None or session.user_id != user_id:
            raise BillingError("Session introuvable.")
        if session.status != VideoAssistanceStatus.REQUESTED:
            raise BillingError(
                f"État invalide pour disclosure: {session.status}"
            )

        session.user_consent = True
        session.disclosed_at = datetime.now(UTC)
        session.status = VideoAssistanceStatus.DISCLOSED
        await self.db.flush()
        logger.info("video.disclosed", session_id=str(session_id))
        return session

    async def start_session(
        self,
        session_id: uuid.UUID,
        agent_id: uuid.UUID,
        agent_name: str,
        video_room_url: str,
        video_provider: str = "jitsi",
    ) -> VideoAssistanceSession:
        """L'agent démarre la session vidéo."""
        session = await self.db.get(VideoAssistanceSession, session_id)
        if session is None:
            raise BillingError("Session introuvable.")
        if session.status != VideoAssistanceStatus.DISCLOSED:
            raise BillingError(
                "Le user doit d'abord confirmer la tarification (disclosure)."
            )

        session.agent_id = agent_id
        session.agent_name = agent_name
        session.video_room_url = video_room_url
        session.video_provider = video_provider
        session.started_at = datetime.now(UTC)
        session.status = VideoAssistanceStatus.IN_PROGRESS
        await self.db.flush()
        return session

    async def end_session_and_bill(
        self, session_id: uuid.UUID
    ) -> tuple[VideoAssistanceSession, OutstandingBill]:
        """Termine la session, calcule la durée, crée la facture en attente."""
        session = await self.db.get(VideoAssistanceSession, session_id)
        if session is None:
            raise BillingError("Session introuvable.")
        if session.status != VideoAssistanceStatus.IN_PROGRESS:
            raise BillingError(
                f"Session pas en cours (status={session.status})"
            )

        now = datetime.now(UTC)
        started = session.started_at
        if started is None:
            raise BillingError("Session jamais démarrée.")
        if started.tzinfo is None:
            started = started.replace(tzinfo=UTC)

        duration_seconds = int((now - started).total_seconds())
        # Arrondi supérieur à la tranche de 10 min
        minutes = max(
            duration_seconds / 60.0,
            float(settings.video_assistance_min_billed_minutes),
        )
        # Plafond
        if minutes > settings.video_assistance_max_session_minutes:
            minutes = float(settings.video_assistance_max_session_minutes)

        billed_chunks = int(math.ceil(minutes / 10.0))
        billed_minutes_rounded = billed_chunks * 10
        billed_amount = billed_chunks * session.rate_kmf_per_10min

        session.ended_at = now
        session.duration_seconds = duration_seconds
        session.billed_minutes_rounded_up = billed_minutes_rounded
        session.billed_amount_kmf = billed_amount
        session.status = VideoAssistanceStatus.COMPLETED

        # Création OutstandingBill
        bill = OutstandingBill(
            tenant_id=session.tenant_id,
            user_id=session.user_id,
            kind=BillKind.VIDEO_ASSISTANCE,
            description=(
                f"Assistance vidéo {billed_minutes_rounded} min "
                f"({duration_seconds // 60} min utilisées) — {now.strftime('%Y-%m-%d')}"
            ),
            amount_kmf=billed_amount,
            status=BillStatus.OUTSTANDING,
            source_video_session_id=session.id,
        )
        self.db.add(bill)
        await self.db.flush()
        session.outstanding_bill_id = bill.id
        await self.db.flush()

        logger.info(
            "video.ended_and_billed",
            session_id=str(session_id),
            duration_s=duration_seconds,
            billed_kmf=billed_amount,
            bill_id=str(bill.id),
        )
        return session, bill

    # ──────────────────────────────────────────────
    #  Outstanding bills — règlement par vendeur
    # ──────────────────────────────────────────────
    async def get_customer_dashboard(self, phone: str) -> CustomerDashboard | None:
        """Snapshot vendeur — appelé dès saisie du numéro client.

        Retourne factures en attente, état compte, éligibilité vidéo.
        """
        result = await self.db.execute(select(User).where(User.phone == phone))
        user = result.scalar_one_or_none()
        if user is None:
            return None

        # Outstanding bills
        result = await self.db.execute(
            select(OutstandingBill).where(
                OutstandingBill.user_id == user.id,
                OutstandingBill.status == BillStatus.OUTSTANDING,
            )
        )
        bills = result.scalars().all()
        total_due = sum(b.amount_kmf for b in bills)

        state_str = (
            user.account_state.value
            if hasattr(user.account_state, "value")
            else str(user.account_state)
        )

        return CustomerDashboard(
            user_id=user.id,
            phone=user.phone,
            account_state=state_str,
            full_name=user.full_name,
            outstanding_bills=list(bills),
            total_due_kmf=total_due,
            eligible_for_video_assistance=(user.account_state == AccountState.ACTIVE),
        )

    async def settle_bills(
        self,
        bill_ids: list[uuid.UUID],
        payment_id: uuid.UUID,
        vendor_id: str,
    ) -> int:
        """Marque des factures comme réglées via un paiement."""
        count = 0
        for bill_id in bill_ids:
            bill = await self.db.get(OutstandingBill, bill_id)
            if bill is None or bill.status != BillStatus.OUTSTANDING:
                continue
            bill.status = BillStatus.SETTLED
            bill.settled_at = datetime.now(UTC)
            bill.settled_via_payment_id = payment_id
            bill.settled_via_vendor_id = vendor_id
            count += 1
        await self.db.flush()
        logger.info(
            "bills.settled",
            count=count,
            payment_id=str(payment_id),
            vendor_id=vendor_id,
        )
        return count
