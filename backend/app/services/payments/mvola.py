"""Provider Mvola (Telma Madagascar / Comores) — stub MVP."""

from __future__ import annotations

import uuid

import structlog

from app.services.payments.base import (
    BasePaymentProvider,
    InitiationResult,
    PaymentProviderError,
    WebhookVerificationResult,
)

logger = structlog.get_logger(__name__)


class MvolaProvider(BasePaymentProvider):
    code = "mvola"

    async def initiate(
        self,
        amount_local: int,
        currency: str,
        phone: str | None,
        reference: str,
        metadata: dict | None = None,
    ) -> InitiationResult:
        if currency != "KMF":
            raise PaymentProviderError(f"Mvola attend KMF, reçu: {currency}")
        if not phone:
            raise PaymentProviderError("Phone client requis.")
        provider_ref = f"MVOLA-{uuid.uuid4().hex[:12].upper()}"
        logger.info("mvola.initiated_stub", provider_ref=provider_ref)
        return InitiationResult(
            provider_ref=provider_ref,
            requires_user_action=True,
            user_action_text="Confirme la transaction Mvola sur ton téléphone.",
            ussd_code=f"#111*{amount_local}#",
            expires_in_seconds=300,
        )

    async def verify_callback(
        self, payload: dict, signature: str | None
    ) -> WebhookVerificationResult:
        # TODO Sprint 3.5 : vérification signature Mvola
        return WebhookVerificationResult(
            is_valid=True,
            provider_ref=payload.get("reference"),
            status=payload.get("status", "success"),
            amount_local=payload.get("amount"),
            currency="KMF",
            raw_payload=payload,
        )
