"""SmsService — envoi SMS OTP via Africa's Talking (marché Comores).

Fallback SMS activé uniquement si WhatsApp indisponible.
Africa's Talking supporte les Comores (+269), Tanzanie, Kenya.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

_AT_SMS_URL = "https://api.africastalking.com/version1/messaging"
_AT_SMS_SANDBOX_URL = "https://api.sandbox.africastalking.com/version1/messaging"


@dataclass(frozen=True)
class SmsDeliveryResult:
    is_sent: bool
    message_id: str | None
    cost: str | None
    error_message: str | None = None


class SmsService:
    """Envoie des SMS OTP via Africa's Talking.

    En dev (sandbox), les SMS sont loggués mais non envoyés réellement.
    En prod, l'API Africa's Talking est appelée avec les credentials configurés.
    """

    def __init__(self) -> None:
        self._is_sandbox = (
            settings.app_env != "prod"
            or settings.africastalking_username == "sandbox"
        )
        self._url = _AT_SMS_SANDBOX_URL if self._is_sandbox else _AT_SMS_URL

    async def send_otp_sms(self, phone: str, otp_code: str) -> SmsDeliveryResult:
        """Envoie un OTP par SMS au numéro indiqué.

        Le message est court (< 160 chars) pour ne pas dépasser 1 unité SMS.
        """
        message = f"Votre code Nasoma : {otp_code}. Valide 5 minutes. Ne le partagez jamais."

        if settings.app_env == "dev" and self._is_sandbox:
            logger.info(
                "sms.otp.dev_stub",
                phone_suffix=phone[-4:],
                code=otp_code,
                message=message,
            )
            return SmsDeliveryResult(
                is_sent=True,
                message_id="dev-stub-id",
                cost="0",
            )

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self._url,
                    headers={
                        "Accept": "application/json",
                        "apiKey": settings.africastalking_api_key,
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    data={
                        "username": settings.africastalking_username,
                        "to": phone,
                        "message": message,
                        "from": settings.africastalking_sender_id,
                    },
                )
                response.raise_for_status()
                data = response.json()

                recipients = (
                    data.get("SMSMessageData", {}).get("Recipients", [])
                )
                if not recipients:
                    logger.error("sms.otp.no_recipients", response=data)
                    return SmsDeliveryResult(
                        is_sent=False,
                        message_id=None,
                        cost=None,
                        error_message="Aucun destinataire dans la réponse Africa's Talking",
                    )

                recipient = recipients[0]
                is_success = recipient.get("statusCode") in (100, 101, 102)

                logger.info(
                    "sms.otp.sent" if is_success else "sms.otp.failed",
                    phone_suffix=phone[-4:],
                    status=recipient.get("status"),
                    status_code=recipient.get("statusCode"),
                    cost=recipient.get("cost"),
                )

                return SmsDeliveryResult(
                    is_sent=is_success,
                    message_id=recipient.get("messageId"),
                    cost=recipient.get("cost"),
                    error_message=None if is_success else recipient.get("status"),
                )

        except httpx.HTTPStatusError as exc:
            logger.error(
                "sms.otp.http_error",
                status_code=exc.response.status_code,
                phone_suffix=phone[-4:],
            )
            return SmsDeliveryResult(
                is_sent=False,
                message_id=None,
                cost=None,
                error_message=f"HTTP {exc.response.status_code}",
            )
        except httpx.RequestError as exc:
            logger.error("sms.otp.request_error", error=str(exc), phone_suffix=phone[-4:])
            return SmsDeliveryResult(
                is_sent=False,
                message_id=None,
                cost=None,
                error_message=str(exc),
            )
