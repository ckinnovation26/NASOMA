"""Abstraction provider de paiement."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class PaymentProviderError(Exception):
    """Erreur métier provider de paiement."""


@dataclass(frozen=True)
class InitiationResult:
    """Résultat d'une initiation de paiement (STK push ou redirect)."""

    provider_ref: str                          # référence unique chez le provider
    requires_user_action: bool                 # True = STK push à confirmer / redirect URL
    user_action_text: str | None = None        # message à afficher
    redirect_url: str | None = None            # pour Stripe (carte)
    ussd_code: str | None = None               # pour MoMo
    expires_in_seconds: int = 300


@dataclass(frozen=True)
class WebhookVerificationResult:
    """Résultat de la vérification d'un webhook provider."""

    is_valid: bool
    provider_ref: str | None
    status: str                                # 'success' | 'failed' | 'pending'
    amount_local: int | None = None
    currency: str | None = None
    raw_payload: dict[str, Any] | None = None


class BasePaymentProvider(ABC):
    """Interface commune pour tous les providers."""

    code: str = ""                             # 'hollo' | 'mvola' | 'stripe'

    @abstractmethod
    async def initiate(
        self,
        amount_local: int,
        currency: str,
        phone: str | None,
        reference: str,
        metadata: dict | None = None,
    ) -> InitiationResult:
        """Initie un paiement et retourne les infos pour l'utilisateur."""

    @abstractmethod
    async def verify_callback(
        self,
        payload: dict,
        signature: str | None,
    ) -> WebhookVerificationResult:
        """Vérifie un webhook reçu du provider (signature HMAC) et extrait l'état."""
