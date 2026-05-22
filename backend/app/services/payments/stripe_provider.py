"""Provider Stripe — cartes diaspora.

⚠️ Stub MVP : nécessite intégration stripe-python en Sprint 3.5.
"""

from __future__ import annotations

import uuid

import structlog

from app.services.payments.base import (
    BasePaymentProvider,
    InitiationResult,
    WebhookVerificationResult,
)

logger = structlog.get_logger(__name__)


class StripeProvider(BasePaymentProvider):
    code = "stripe"

    async def initiate(
        self,
        amount_local: int,
        currency: str,
        phone: str | None,
        reference: str,
        metadata: dict | None = None,
    ) -> InitiationResult:
        """Initie un Stripe Checkout Session."""
        provider_ref = f"STRIPE-{uuid.uuid4().hex[:12].upper()}"

        # TODO Sprint 3.5 : appel réel stripe.checkout.Session.create()
        # session = stripe.checkout.Session.create(
        #     payment_method_types=["card"],
        #     line_items=[{
        #         "price_data": {
        #             "currency": currency.lower(),
        #             "product_data": {"name": "Nasoma — Recharge"},
        #             "unit_amount": amount_local,
        #         },
        #         "quantity": 1,
        #     }],
        #     mode="payment",
        #     success_url="...",
        #     cancel_url="...",
        #     client_reference_id=reference,
        # )
        # redirect_url = session.url

        redirect_url = f"https://nasoma.app/checkout/{provider_ref}"

        logger.info("stripe.initiated_stub", provider_ref=provider_ref, amount=amount_local)
        return InitiationResult(
            provider_ref=provider_ref,
            requires_user_action=True,
            user_action_text="Vous serez redirigé vers la page de paiement.",
            redirect_url=redirect_url,
            expires_in_seconds=1800,
        )

    async def verify_callback(
        self, payload: dict, signature: str | None
    ) -> WebhookVerificationResult:
        """Vérifie un webhook Stripe (signature header `Stripe-Signature`)."""
        # TODO Sprint 3.5 : stripe.Webhook.construct_event() avec STRIPE_WEBHOOK_SECRET
        event_type = payload.get("type", "")
        is_success = event_type == "checkout.session.completed"
        data = payload.get("data", {}).get("object", {})
        return WebhookVerificationResult(
            is_valid=True,                              # stub MVP
            provider_ref=data.get("client_reference_id"),
            status="success" if is_success else "pending",
            amount_local=data.get("amount_total"),
            currency=(data.get("currency") or "").upper() or None,
            raw_payload=payload,
        )
