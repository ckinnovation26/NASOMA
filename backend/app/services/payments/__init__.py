"""Module payments — providers MoMo (Hollo, Mvola) + Stripe (diaspora).

Architecture :
- BaseProvider (abstract)
- HolloProvider (Comores Telecom)
- MvolaProvider (Telma)
- StripeProvider (cartes diaspora)

Tous implémentent : initiate(), verify_callback().
"""

from app.services.payments.base import (
    BasePaymentProvider,
    InitiationResult,
    PaymentProviderError,
    WebhookVerificationResult,
)
from app.services.payments.hollo import HolloProvider
from app.services.payments.mvola import MvolaProvider
from app.services.payments.stripe_provider import StripeProvider

__all__ = [
    "BasePaymentProvider",
    "HolloProvider",
    "InitiationResult",
    "MvolaProvider",
    "PaymentProviderError",
    "StripeProvider",
    "WebhookVerificationResult",
]


def get_provider(name: str) -> BasePaymentProvider:
    """Factory : retourne une instance du provider demandé."""
    mapping: dict[str, type[BasePaymentProvider]] = {
        "hollo": HolloProvider,
        "mvola": MvolaProvider,
        "stripe": StripeProvider,
    }
    cls = mapping.get(name.lower())
    if cls is None:
        raise ValueError(f"Provider inconnu: {name}")
    return cls()
