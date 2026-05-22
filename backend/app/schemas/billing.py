"""Schémas Pydantic — billing post-paid + vendor dashboard."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
#  Video assistance
# ──────────────────────────────────────────────
class VideoAssistanceRequestPayload(BaseModel):
    """Demande d'assistance vidéo — vérification ACTIVE en backend."""

    student_id: uuid.UUID


class FreeAlternativeVendor(BaseModel):
    """Vendeur recommandé pour assistance GRATUITE en personne."""

    vendor_id: uuid.UUID
    code: str
    name: str
    contact_phone: str
    distance_km: float | None = None
    city: str | None = None
    relationship: Literal["usual_vendor", "nearest_active", "any_active"] = "usual_vendor"
    is_trained_level1: bool


class VideoAssistanceDisclosureResponse(BaseModel):
    """Réponse contenant l'ALTERNATIVE GRATUITE PUIS les conditions tarifaires.

    L'app DOIT présenter dans l'ordre :
    1. L'option gratuite chez le vendeur habituel (free_alternative_text + vendor)
    2. Si l'utilisateur refuse l'option gratuite et veut quand même la vidéo payante :
       afficher disclosure_text + récolter user_consent
    """

    session_id: uuid.UUID
    free_alternative_text: str
    free_alternative_vendor: FreeAlternativeVendor | None = None
    rate_kmf_per_10min: int
    max_session_minutes: int
    disclosure_text: str
    consent_required: bool = True
    next_step: str = "POST /support/video-assistance/{session_id}/confirm pour démarrer"


class VideoAssistanceConfirmPayload(BaseModel):
    user_consent: Literal[True]                  # doit être True explicite


class VideoAssistanceStartedResponse(BaseModel):
    session_id: uuid.UUID
    video_room_url: str
    agent_name: str
    started_at: datetime


class VideoAssistanceEndedResponse(BaseModel):
    session_id: uuid.UUID
    duration_seconds: int
    billed_minutes: int
    billed_amount_kmf: int
    outstanding_bill_id: uuid.UUID
    message: str


# ──────────────────────────────────────────────
#  Vendor dashboard
# ──────────────────────────────────────────────
class OutstandingBillPublic(BaseModel):
    bill_id: uuid.UUID
    kind: str
    description: str
    amount_kmf: int
    created_at: datetime
    grace_until: datetime | None = None


class VendorCustomerDashboardResponse(BaseModel):
    """Snapshot client affiché au vendeur dès saisie du numéro.

    ⚠️ Le vendeur DOIT présenter ces informations au client AVANT toute
    transaction et lui faire choisir explicitement entre :
    - Régler les factures uniquement
    - Recharger un service uniquement
    - Les deux
    """

    user_id: uuid.UUID
    phone: str
    full_name: str | None
    account_state: Literal["active", "grace", "frozen", "archived"]
    outstanding_bills: list[OutstandingBillPublic]
    total_due_kmf: int
    eligible_for_video_assistance: bool
    available_plans: list[str]
    home_city: str | None = None
    home_island: str | None = None


class VendorRechargePayload(BaseModel):
    """Le vendeur enregistre une transaction.

    Doit indiquer si le client règle des dettes, recharge un plan, ou les deux.
    """

    phone: str
    settle_bill_ids: list[uuid.UUID] = Field(default_factory=list)
    new_plan: Literal["daily", "three_day", "weekly", "monthly"] | None = None
    amount_received_kmf: int = Field(..., ge=0)
    vendor_code: str
    notes: str | None = None


class VendorRechargeResponse(BaseModel):
    payment_id: uuid.UUID
    bills_settled_count: int
    bills_settled_total_kmf: int
    new_subscription_id: uuid.UUID | None = None
    new_otp_code: str | None = None              # pour ticket physique
    receipt_text: str


# ──────────────────────────────────────────────
#  Diaspora purchase recommendation
# ──────────────────────────────────────────────
class DiasporaPurchaseRequest(BaseModel):
    """Achat depuis le portail web diaspora (Stripe etc.)."""

    target_child_phone: str
    plan: Literal["daily", "three_day", "weekly", "monthly"]
    payer_email: str
    payer_country: str | None = None             # ex: "FR", "AE", "YT"


class VendorNearbyRecommendation(BaseModel):
    vendor_id: uuid.UUID
    code: str
    name: str
    contact_phone: str
    distance_km: float | None = None
    city: str | None = None
    island: str | None = None
    is_trained_level1: bool


class DiasporaPurchaseResponse(BaseModel):
    payment_id: uuid.UUID
    target_child_phone: str
    plan: str
    otp_code: str                               # à transmettre via WhatsApp à l'enfant
    nearby_vendors_for_assistance: list[VendorNearbyRecommendation]
    message: str = (
        "Achat effectué. Si votre enfant a besoin d'aide physique, "
        "voici les vendeurs proches de chez lui."
    )
