"""Service ScanQuality — détecte les patterns d'échec récurrent et déclenche l'assistance.

Logique :
- Si > 3 scans avec status DONE_WITH_FALLBACK ou FAILED en 7j → proposer assistance vendeur
- Identifie le dernier vendeur du user (via payments) pour notification
- Crée une VendorAssistanceRequest
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fallback import (
    AssistanceReason,
    AssistanceStatus,
    VendorAssistanceRequest,
)
from app.models.payments import Payment, PaymentStatus
from app.models.scans import Scan, ScanStatus

logger = structlog.get_logger(__name__)

RECURRENCE_WINDOW_DAYS = 7
RECURRENCE_THRESHOLD = 3
ASSISTANCE_REOFFER_COOLDOWN_DAYS = 7


class ScanQualityService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def count_failed_scans_last_7d(self, user_id: uuid.UUID) -> int:
        """Compte les scans DONE_WITH_FALLBACK ou FAILED dans les 7 derniers jours."""
        cutoff = datetime.now(UTC) - timedelta(days=RECURRENCE_WINDOW_DAYS)
        stmt = (
            select(func.count())
            .select_from(Scan)
            .where(
                Scan.student_id == user_id,
                Scan.status.in_([ScanStatus.DONE_WITH_FALLBACK, ScanStatus.FAILED]),
                Scan.created_at >= cutoff,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one() or 0

    async def should_propose_assistance(self, user_id: uuid.UUID) -> bool:
        """Vérifie si on doit proposer l'assistance (et qu'on n'a pas déjà proposé < 7j)."""
        failed_count = await self.count_failed_scans_last_7d(user_id)
        if failed_count < RECURRENCE_THRESHOLD:
            return False

        # Anti-spam : pas re-proposer dans les 7j si déjà demandé
        cutoff = datetime.now(UTC) - timedelta(days=ASSISTANCE_REOFFER_COOLDOWN_DAYS)
        stmt = select(VendorAssistanceRequest).where(
            VendorAssistanceRequest.user_id == user_id,
            VendorAssistanceRequest.created_at >= cutoff,
        )
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none() is not None:
            return False

        return True

    async def get_last_vendor_id(self, user_id: uuid.UUID) -> str | None:
        """Récupère l'ID du dernier vendeur qui a servi ce user (via payments)."""
        stmt = (
            select(Payment.vendor_id)
            .where(
                Payment.user_id == user_id,
                Payment.status == PaymentStatus.SUCCESS,
                Payment.vendor_id.isnot(None),
            )
            .order_by(Payment.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_assistance_request(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        reason: AssistanceReason,
    ) -> VendorAssistanceRequest:
        """Crée une demande d'assistance vendeur."""
        vendor_id = await self.get_last_vendor_id(user_id)
        failed_count = await self.count_failed_scans_last_7d(user_id)

        request = VendorAssistanceRequest(
            tenant_id=tenant_id,
            user_id=user_id,
            vendor_id=vendor_id,
            reason=reason,
            failed_scans_count_7d=failed_count,
            status=AssistanceStatus.PENDING,
        )
        self.db.add(request)
        await self.db.flush()

        logger.info(
            "assistance.requested",
            request_id=str(request.id),
            user_id=str(user_id),
            vendor_id=vendor_id,
            reason=reason.value,
            failed_count=failed_count,
        )

        # TODO Sprint 2.5 : notifier le vendeur (push interne + email)
        return request

    @staticmethod
    def extract_keywords(parent_comment: str | None) -> str | None:
        """Stub Sprint 2 — extraction de mots-clés du commentaire parent.

        Sprint 2.5 : appel Gemini Flash pour extraction sémantique.
        Pour MVP, simple tokenization basique.
        """
        if not parent_comment:
            return None
        words = [w.lower() for w in parent_comment.split() if len(w) > 3]
        return ",".join(words[:10])
