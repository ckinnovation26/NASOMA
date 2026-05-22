"""Provider Hollo Money (Comores Telecom) — STK push via API partenaire.

Intégration : API REST Hollo Money.
Docs internes : à valider avec Comores Telecom avant sprint 3.
Sandbox : https://sandbox.hollo.km/v1 (credentials test fournis par Hollo)
Prod    : https://api.hollo.km/v1

Flow STK push :
  1. POST /collections → Hollo envoie une invite de paiement sur le téléphone du client
  2. Client confirme avec son PIN Hollo
  3. Hollo appelle le webhook (X-Hollo-Signature HMAC-SHA256)
  4. Backend vérifie la signature → active la subscription
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from typing import Any

import httpx
import structlog

from app.core.config import settings
from app.services.payments.base import (
    BasePaymentProvider,
    InitiationResult,
    PaymentProviderError,
    WebhookVerificationResult,
)

logger = structlog.get_logger(__name__)

_HOLLO_SANDBOX_URL = "https://sandbox.hollo.km/v1"
_HOLLO_PROD_URL = "https://api.hollo.km/v1"
_TIMEOUT_SECONDS = 15.0


class HolloProvider(BasePaymentProvider):
    """Hollo Money (Comores Telecom) — STK push."""

    code = "hollo"

    def __init__(self) -> None:
        self._base_url = (
            _HOLLO_SANDBOX_URL if settings.app_env != "prod" else _HOLLO_PROD_URL
        )

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
            raise PaymentProviderError("Numéro de téléphone client requis pour STK push.")
        if not settings.hollo_api_key or not settings.hollo_merchant_id:
            # Sandbox : simuler sans appel réseau
            return self._sandbox_initiation(amount_local, phone, reference)

        provider_ref = f"HOLLO-{uuid.uuid4().hex[:12].upper()}"
        callback_url = f"{settings.api_base_url}/api/v1/payments/webhook/hollo"

        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    f"{self._base_url}/collections",
                    headers={
                        "Authorization": f"Bearer {settings.hollo_api_key}",
                        "X-Merchant-ID": settings.hollo_merchant_id,
                        "Content-Type": "application/json",
                    },
                    json={
                        "amount": amount_local,
                        "currency": "KMF",
                        "customer_msisdn": phone,
                        "external_ref": reference,
                        "provider_ref": provider_ref,
                        "callback_url": callback_url,
                        "description": "Abonnement Nasoma",
                        **(metadata or {}),
                    },
                )
                response.raise_for_status()
                data = response.json()

        except httpx.HTTPStatusError as exc:
            logger.error(
                "hollo.initiate.http_error",
                status_code=exc.response.status_code,
                body=exc.response.text[:200],
            )
            raise PaymentProviderError(
                f"Hollo API HTTP {exc.response.status_code}: {exc.response.text[:100]}"
            ) from exc
        except httpx.RequestError as exc:
            logger.error("hollo.initiate.network_error", error=str(exc))
            raise PaymentProviderError(f"Réseau Hollo inaccessible: {exc}") from exc

        # Hollo retourne transaction_id + status (pending / approved / failed)
        api_status = data.get("status", "pending")
        if api_status == "failed":
            raise PaymentProviderError(
                data.get("message", "Initiation Hollo refusée.")
            )

        hollo_ref = data.get("transaction_id", provider_ref)

        logger.info(
            "hollo.initiated",
            amount=amount_local,
            phone_suffix=phone[-4:],
            provider_ref=hollo_ref,
            status=api_status,
        )
        return InitiationResult(
            provider_ref=hollo_ref,
            requires_user_action=True,
            user_action_text=(
                f"Une invitation de paiement de {amount_local:,} KMF a été envoyée "
                f"à ton Hollo Money ({phone[-4:]}).\n"
                "Confirme avec ton code PIN Hollo."
            ),
            ussd_code=None,
            expires_in_seconds=300,
        )

    async def verify_callback(
        self,
        payload: dict,
        signature: str | None,
    ) -> WebhookVerificationResult:
        """Vérifie la signature HMAC-SHA256 du webhook Hollo."""
        expected = self._compute_signature(payload)
        is_valid = bool(signature) and hmac.compare_digest(expected, signature or "")

        if not is_valid:
            logger.warning(
                "hollo.webhook.invalid_signature",
                received=signature[:16] if signature else "None",
                expected_prefix=expected[:16],
            )
            return WebhookVerificationResult(
                is_valid=False,
                provider_ref=payload.get("transaction_id") or payload.get("provider_ref"),
                status="failed",
                raw_payload=payload,
            )

        # Mapper les statuts Hollo vers le standard interne
        raw_status = payload.get("status", "")
        internal_status = self._map_status(raw_status)

        amount_raw = payload.get("amount")
        try:
            amount = int(amount_raw) if amount_raw is not None else None
        except (TypeError, ValueError):
            amount = None

        logger.info(
            "hollo.webhook.verified",
            provider_ref=payload.get("transaction_id"),
            status=internal_status,
            amount=amount,
        )
        return WebhookVerificationResult(
            is_valid=True,
            provider_ref=payload.get("transaction_id") or payload.get("external_ref"),
            status=internal_status,
            amount_local=amount,
            currency="KMF",
            raw_payload=payload,
        )

    # ──────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────

    def _compute_signature(self, payload: dict[str, Any]) -> str:
        """HMAC-SHA256 sur le JSON canonique (clés triées, pas d'espaces)."""
        body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hmac.new(
            settings.hollo_webhook_secret.encode(),
            body.encode(),
            hashlib.sha256,
        ).hexdigest()

    def _map_status(self, hollo_status: str) -> str:
        """Traduit les statuts Hollo vers success/failed/pending."""
        mapping = {
            "approved": "success",
            "success": "success",
            "completed": "success",
            "failed": "failed",
            "rejected": "failed",
            "cancelled": "failed",
            "pending": "pending",
            "processing": "pending",
        }
        return mapping.get(hollo_status.lower(), "pending")

    def _sandbox_initiation(
        self,
        amount_local: int,
        phone: str,
        reference: str,
    ) -> InitiationResult:
        """Simule l'initiation sans API key (env dev/staging sans credentials)."""
        provider_ref = f"HOLLO-SANDBOX-{uuid.uuid4().hex[:10].upper()}"
        logger.info(
            "hollo.sandbox_stub",
            amount=amount_local,
            phone_suffix=phone[-4:],
            ref=provider_ref,
        )
        return InitiationResult(
            provider_ref=provider_ref,
            requires_user_action=True,
            user_action_text=(
                f"[SANDBOX] Paiement de {amount_local:,} KMF simulé. "
                f"Ref: {provider_ref}"
            ),
            ussd_code=None,
            expires_in_seconds=300,
        )
