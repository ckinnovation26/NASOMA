"""CommunicationService — route les OTP et notifications par le bon canal.

Règle métier (décision 2026-05-20) :
- 1ère inscription d'un numéro → **WhatsApp** (multimédia onboarding + KYC)
- Renouvellements suivants → **Push FCM in-app** (gratuit, app toujours installée)
- Désinstall détecté ou push échoué après N jours → **WhatsApp fallback**
- SMS (Africa's Talking / Twilio) → fallback ultime si WhatsApp indispo

Aucun coût récurrent SMS. WhatsApp utilisé uniquement aux moments stratégiques.
"""

from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.services.whatsapp_service import WhatsAppService

logger = structlog.get_logger(__name__)


class OtpChannel(str, enum.Enum):
    WHATSAPP = "whatsapp"
    PUSH_FCM = "push_fcm"
    SMS_FALLBACK = "sms_fallback"
    VENDOR_DISPLAY = "vendor_display"      # vendeur lit/montre le code en main propre


@dataclass(frozen=True)
class DeliveryDecision:
    channel: OtpChannel
    reason: str
    cost_estimate_usd: float


class CommunicationService:
    """Route les communications vers le canal le moins cher et le plus fiable."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.whatsapp = WhatsAppService()

    async def decide_otp_channel(
        self, user: User, is_first_signup: bool, has_app_installed: bool
    ) -> DeliveryDecision:
        """Décide quel canal utiliser pour livrer un OTP."""
        if is_first_signup:
            return DeliveryDecision(
                channel=OtpChannel.WHATSAPP,
                reason="first_signup_multimedia_onboarding",
                cost_estimate_usd=0.01,
            )
        if has_app_installed:
            return DeliveryDecision(
                channel=OtpChannel.PUSH_FCM,
                reason="app_installed_use_free_channel",
                cost_estimate_usd=0.0,
            )
        # App désinstallée → WhatsApp re-engagement
        return DeliveryDecision(
            channel=OtpChannel.WHATSAPP,
            reason="app_uninstalled_reengagement",
            cost_estimate_usd=0.01,
        )

    async def send_first_signup_otp(
        self,
        user: User,
        otp_code: str,
        free_scans: int,
        ttl_days: int,
    ) -> bool:
        """Envoi WhatsApp avec onboarding multimédia complet (1ère inscription)."""
        result = await self.whatsapp.send_first_signup_otp(
            phone=user.phone,
            otp_code=otp_code,
            full_name=user.full_name,
            free_scans=free_scans,
            ttl_days=ttl_days,
        )
        logger.info(
            "communication.first_otp_sent",
            user_id=str(user.id),
            channel="whatsapp",
            sent=result.is_sent,
            cost_usd=result.cost_estimate_usd,
        )
        return result.is_sent

    async def send_renewal_otp(
        self,
        user: User,
        otp_code: str,
        plan: str,
        has_app_installed: bool = True,
    ) -> bool:
        """OTP de renouvellement — Push FCM si app installée, WhatsApp sinon."""
        decision = await self.decide_otp_channel(
            user, is_first_signup=False, has_app_installed=has_app_installed
        )

        if decision.channel == OtpChannel.PUSH_FCM:
            # TODO Sprint 3.5 : envoyer push FCM avec data payload
            logger.info(
                "communication.renewal_push_DEV_STUB",
                user_id=str(user.id),
                code=otp_code,
            )
            return True

        # Fallback WhatsApp
        result = await self.whatsapp.send_marketing(
            phone=user.phone,
            full_name=user.full_name,
            message_body=(
                f"Bonjour {user.full_name or 'Ami'}, ton nouveau code Nasoma : {otp_code}\n"
                f"Plan : {plan}. Ouvre l'app pour activer."
            ),
        )
        return result.is_sent

    async def send_reengagement(
        self, user: User, days_since_uninstall: int
    ) -> bool:
        """Re-engagement WhatsApp pour user qui a désinstallé."""
        result = await self.whatsapp.send_reengagement(
            phone=user.phone,
            full_name=user.full_name,
            days_since_uninstall=days_since_uninstall,
        )
        return result.is_sent
