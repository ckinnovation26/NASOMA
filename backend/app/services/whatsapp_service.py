"""WhatsApp Business API — canal primaire OTP + onboarding multimédia.

Décision (2026-05-20) :
- WhatsApp = canal OTP de 1ère inscription (multimédia, ~3× moins cher que SMS)
- App in-app + push FCM = canal post-activation (gratuit)
- WhatsApp = fallback si désinstallation détectée (re-engagement)

Providers supportés (au choix selon coût Comores) :
- 360Dialog Africa
- Twilio WhatsApp
- Meta Business Cloud API direct

⚠️ Stub Sprint 3 — vraie intégration Sprint 3.5 avec API choisie.
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class WhatsAppDeliveryResult:
    """Résultat d'un envoi WhatsApp."""

    is_sent: bool
    provider_message_id: str | None
    cost_estimate_usd: float
    error_message: str | None = None


class WhatsAppService:
    """Envoi messages WhatsApp via Business API (stub MVP).

    Avantages vs SMS :
    - Coût ~0,005-0,015 $ (vs 0,02 $ SMS Africa's Talking)
    - Multimédia : vidéo onboarding, images, liens cliquables, boutons
    - Délivrabilité confirmée (statut "lu" possible)
    - Templates pré-approuvés pour OTP (compliance Meta)
    """

    async def send_first_signup_otp(
        self,
        phone: str,
        otp_code: str,
        full_name: str | None,
        free_scans: int,
        ttl_days: int,
        download_app_url: str = "https://nasoma.app/download",
        onboarding_video_url: str = "https://nasoma.app/onboarding.mp4",
    ) -> WhatsAppDeliveryResult:
        """Envoie le 1er OTP avec pack onboarding complet.

        Template type : 'nasoma_first_signup_fr' (à approuver côté Meta).
        Contenu :
        - Bienvenue {full_name}
        - Code OTP {otp_code}
        - {free_scans} scans gratuits valables {ttl_days} jours
        - Lien téléchargement app (image preview)
        - Vidéo onboarding 2 min
        - Instructions step-by-step
        """
        if settings.app_env == "dev":
            logger.info(
                "whatsapp.first_signup_DEV_STUB",
                phone_suffix=phone[-4:],
                code=otp_code,
                full_name=full_name,
                free_scans=free_scans,
            )
            return WhatsAppDeliveryResult(
                is_sent=True,
                provider_message_id=f"DEV-{phone[-4:]}-{otp_code}",
                cost_estimate_usd=0.0,
            )

        # TODO Sprint 3.5 : implémentation réelle 360Dialog/Twilio/Meta
        # POST https://waba.360dialog.io/v1/messages
        # {
        #   "to": phone, "type": "template",
        #   "template": {
        #     "name": "nasoma_first_signup_fr",
        #     "language": {"code": "fr"},
        #     "components": [
        #       {"type": "header", "parameters": [{"type": "video", "video": {"link": video_url}}]},
        #       {"type": "body", "parameters": [
        #         {"type": "text", "text": full_name},
        #         {"type": "text", "text": otp_code},
        #         {"type": "text", "text": str(free_scans)},
        #         {"type": "text", "text": str(ttl_days)},
        #       ]},
        #       {"type": "button", "sub_type": "url", "index": 0,
        #        "parameters": [{"type": "text", "text": download_app_url}]},
        #     ]
        #   }
        # }
        raise NotImplementedError("Intégration WhatsApp Business API à finaliser Sprint 3.5")

    async def send_reengagement(
        self,
        phone: str,
        full_name: str | None,
        days_since_uninstall: int,
        reinstall_url: str = "https://nasoma.app/download",
    ) -> WhatsAppDeliveryResult:
        """Re-engagement WhatsApp si app désinstallée (fallback uniquement).

        Template : 'nasoma_reengagement_fr' (approuvé Meta).
        """
        if settings.app_env == "dev":
            logger.info(
                "whatsapp.reengagement_DEV_STUB",
                phone_suffix=phone[-4:],
                days=days_since_uninstall,
            )
            return WhatsAppDeliveryResult(
                is_sent=True,
                provider_message_id=f"DEV-RE-{phone[-4:]}",
                cost_estimate_usd=0.0,
            )
        raise NotImplementedError("Intégration WhatsApp Sprint 3.5")

    async def send_marketing(
        self,
        phone: str,
        full_name: str | None,
        message_body: str,
        cta_url: str | None = None,
    ) -> WhatsAppDeliveryResult:
        """Marketing WhatsApp — usage modéré (coût + conformité Meta)."""
        if settings.app_env == "dev":
            logger.info(
                "whatsapp.marketing_DEV_STUB",
                phone_suffix=phone[-4:],
                preview=message_body[:60],
            )
            return WhatsAppDeliveryResult(
                is_sent=True,
                provider_message_id=f"DEV-MKT-{phone[-4:]}",
                cost_estimate_usd=0.0,
            )
        raise NotImplementedError("Sprint 3.5")
