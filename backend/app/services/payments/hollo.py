"""Provider Hollo Money (Comores Telecom) — STK push.

⚠️ Stub MVP : la vraie API Hollo nécessite un partenariat + docs.
Pour Sprint 3, simulation logique.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from typing import Any

import structlog

from app.core.config import settings
from app.services.payments.base import (
    BasePaymentProvider,
    InitiationResult,
    PaymentProviderError,
    WebhookVerificationResult,
)

logger = structlog.get_logger(__name__)


class HolloProvider(BasePaymentProvider):
    """Hollo Money — Comores. Modèle STK push."""

    code = "hollo"

    async def initiate(
        self,
        amount_local: int,
        currency: str,
        phone: str | None,
        reference: str,
        metadata: dict | None = None,
    ) -> InitiationResult:
        if currency != "KMF":
            raise PaymentProviderError(f"Hollo ne supporte que KMF, reçu: {currency}")
        if not phone:
            raise PaymentProviderError("Phone client requis pour Hollo STK push.")

        provider_ref = f"HOLLO-{uuid.uuid4().hex[:12].upper()}"

        # TODO Sprint 3.5 : appel réel API Hollo
        # response = await httpx.post(
        #   "https://api.hollo.km/v1/payments",
        #   headers={"Authorization": f"Bearer {settings.hollo_api_key}"},
        #   json={
        #     "amount": amount_local, "currency": "KMF",
        #     "customer_phone": phone,
        #     "reference": reference,
        #     "callback_url": f"{settings.api_base_url}/api/v1/payments/webhook/hollo"
        #   },
        # )

        logger.info(
            "hollo.initiated_stub",
            amount=amount_local,
            phone_suffix=phone[-4:],
            provider_ref=provider_ref,
        )
        return InitiationResult(
            provider_ref=provider_ref,
            requires_user_action=True,
            user_action_text=(
                f"Compose *123*{amount_local}# sur ton téléphone Hollo "
                "et confirme avec ton code PIN."
            ),
            ussd_code=f"*123*{amount_local}#",
            expires_in_seconds=300,
        )

    async def verify_callback(
        self,
        payload: dict,
        signature: str | None,
    ) -> WebhookVerificationResult:
        if not settings.hollo_webhook_secret:
            logger.warning("hollo.webhook_secret_missing")

        # Vérification HMAC (stub — adapter selon spec Hollo réelle)
        expected = self._compute_signature(payload)
        is_valid = bool(signature) and hmac.compare_digest(expected, signature or "")

        if not is_valid:
            logger.warning("hollo.webhook_invalid_signature")
            return WebhookVerificationResult(
                is_valid=False,
                provider_ref=payload.get("provider_ref"),
                status="failed",
                raw_payload=payload,
            )

        return WebhookVerificationResult(
            is_valid=True,
            provider_ref=payload.get("reference") or payload.get("provider_ref"),
            status=payload.get("status", "success"),
            amount_local=payload.get("amount"),
            currency="KMF",
            raw_payload=payload,
        )

    def _compute_signature(self, payload: dict[str, Any]) -> str:
        body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hmac.new(
            settings.hollo_webhook_secret.encode(),
            body.encode(),
            hashlib.sha256,
        ).hexdigest()
