"""Schémas Pydantic — vendor & diaspora customer signup avec KYC + WhatsApp OTP."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


# ──────────────────────────────────────────────
#  Vendor signup customer (1ère inscription en personne)
# ──────────────────────────────────────────────
class VendorSignupCustomerForm(BaseModel):
    """Le vendeur enregistre un nouveau client en personne.

    Multipart upload : ce schéma + 1 image multipart 'guardian_id_image'.

    ⚠️ Règles 2026-05-20 :
    1. WhatsApp OBLIGATOIRE — le vendeur vérifie que l'enfant a WhatsApp installé
    2. 1 SEULE pièce d'identité = celle du parent/tuteur qui gère le compte
       (responsable légal). Jamais celle de l'enfant directement.
    """

    phone: str                                         # numéro de l'enfant (= identifiant)
    full_name: str = Field(..., min_length=2, max_length=120, description="Nom de l'enfant")
    grade_level: Literal["CM1", "CM2", "6E"] | None = None
    home_city: str | None = None
    home_island: Literal["Ngazidja", "Anjouan", "Mohéli"] | None = None

    # Parent/tuteur — responsable légal du compte
    guardian_full_name: str = Field(..., min_length=2, max_length=120)
    guardian_document_type: Literal["cni", "passport"] = "cni"
    guardian_relationship: Literal["parent", "tuteur", "famille_proche"]

    vendor_code: str = Field(..., min_length=3)
    customer_has_whatsapp: Literal[True] = Field(
        ...,
        description="Le vendeur a vérifié que le client a WhatsApp installé. OBLIGATOIRE.",
    )
    consent_data_processing: Literal[True] = Field(
        ..., description="Le parent/tuteur confirme avoir consenti au traitement RGPD"
    )


class VendorSignupCustomerResponse(BaseModel):
    user_id: uuid.UUID
    phone: str
    otp_code_for_vendor_backup: str            # Vendeur peut lire à voix haute si WhatsApp tarde
    whatsapp_delivery_status: Literal["sent", "failed", "skipped"]
    free_trial_scans: int
    free_trial_expires_at: datetime
    identity_document_id: uuid.UUID
    kyc_status: str
    message: str


# ──────────────────────────────────────────────
#  Diaspora signup customer (1er achat avec KYC)
# ──────────────────────────────────────────────
class DiasporaSignupCustomerForm(BaseModel):
    """Parent diaspora enregistre un enfant au pays (1er achat).

    Upload : 1 SEULE image multipart 'guardian_id_image' = pièce du parent/tuteur
    diaspora qui paye et qui est le responsable légal du compte.

    ⚠️ Règles 2026-05-20 :
    1. WhatsApp OBLIGATOIRE sur le téléphone de l'enfant au pays
    2. 1 SEULE pièce = celle du PARENT/TUTEUR diaspora (qui paye, responsable légal).
       Pas de pièce de l'enfant. Simplifie compliance RGPD/COPPA.
    """

    target_child_phone: str                            # numéro enfant au pays
    child_full_name: str = Field(..., min_length=2, max_length=120)
    child_grade_level: Literal["CM1", "CM2", "6E"] | None = None
    child_home_city: str | None = None
    child_home_island: Literal["Ngazidja", "Anjouan", "Mohéli"] | None = None

    # Parent/tuteur diaspora — responsable légal
    guardian_full_name: str = Field(..., min_length=2, max_length=120)
    guardian_document_type: Literal["cni", "passport"] = "passport"
    guardian_relationship: Literal["parent", "tuteur", "famille_proche"]

    plan: Literal["daily", "three_day", "weekly", "monthly"]
    payer_email: EmailStr
    payer_country: str | None = None
    child_has_whatsapp: Literal[True] = Field(
        ...,
        description=(
            "Le payeur confirme que l'enfant a WhatsApp installé. OBLIGATOIRE — "
            "sans WhatsApp, l'enfant ne peut pas recevoir l'OTP."
        ),
    )
    consent_data_processing: Literal[True]


class DiasporaSignupCustomerResponse(BaseModel):
    user_id: uuid.UUID
    target_child_phone: str
    payment_id: uuid.UUID
    payment_redirect_url: str | None = None
    otp_code: str                              # transmis via WhatsApp à l'enfant
    whatsapp_delivery_status: Literal["sent", "failed", "skipped"]
    identity_document_id: uuid.UUID
    nearby_vendors_for_assistance: list[dict] = []
    message: str = (
        "Achat effectué. Code OTP envoyé via WhatsApp à votre enfant. "
        "Conservez la pièce d'identité scannée."
    )


# ──────────────────────────────────────────────
#  Self signup (depuis app mobile, sans vendeur)
# ──────────────────────────────────────────────
class SelfSignupPayload(BaseModel):
    """Self-signup depuis l'app — pré-check WhatsApp obligatoire.

    Avant tout envoi WhatsApp, on demande au user de confirmer qu'il a
    WhatsApp installé. Sinon, on l'oriente vers un vendeur (Moat distribution)
    ou on lui demande d'installer WhatsApp d'abord.

    Raison : éviter les coûts API WhatsApp à perte + garantir un canal de
    relance ultérieur (re-engagement, marketing, support).
    """

    phone: str
    full_name: str = Field(..., min_length=2, max_length=120)
    has_whatsapp: bool = Field(
        ..., description="Confirmation que le user a WhatsApp installé"
    )
    grade_level: Literal["CM1", "CM2", "6E"] | None = None
    user_latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    user_longitude: float | None = Field(default=None, ge=-180.0, le=180.0)
    home_city: str | None = None
    home_island: Literal["Ngazidja", "Anjouan", "Mohéli"] | None = None
    device_id: str | None = None
    consent_data_processing: Literal[True]


class WhatsAppGuidanceResponse(BaseModel):
    """Réponse quand has_whatsapp=False — orienter vers vendeur ou installation."""

    accepted: Literal[False] = False
    requires_whatsapp_install: Literal[True] = True
    guidance_text: str = (
        "Pour activer Nasoma, tu as besoin de WhatsApp. "
        "Va voir un vendeur Nasoma près de chez toi pour t'aider à l'installer, "
        "ou installe WhatsApp d'abord puis reviens nous voir."
    )
    nearby_vendors: list[dict] = []                 # vendeurs proches via GPS
    download_whatsapp_url_android: str = "https://play.google.com/store/apps/details?id=com.whatsapp"


class SelfSignupAcceptedResponse(BaseModel):
    """Réponse quand has_whatsapp=True — OTP envoyé."""

    accepted: Literal[True] = True
    user_id: uuid.UUID
    phone: str
    free_trial_scans: int
    free_trial_expires_at: datetime
    whatsapp_delivery_status: Literal["sent", "failed"]
    kyc_status: Literal["not_verified"]            # self-signup = pas de pièce
    next_step: str = (
        "Tu as reçu un code via WhatsApp. Entre-le dans l'écran suivant pour activer."
    )
