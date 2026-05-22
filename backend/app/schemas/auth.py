"""Schémas Pydantic — endpoints d'authentification."""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.models.users import AccountState, UserRole

# Validation numéro téléphone E.164 (ex: +269XXXXXXXX)
PHONE_REGEX = re.compile(r"^\+\d{8,15}$")


def _validate_phone(v: str) -> str:
    """Normalise et valide un numéro de téléphone E.164."""
    cleaned = v.replace(" ", "").replace("-", "")
    if not PHONE_REGEX.match(cleaned):
        raise ValueError("Numéro invalide (format E.164 attendu, ex: +269XXXXXXXX)")
    return cleaned


# ──────────────────────────────────────────────
#  Signup SMS (1ère inscription)
# ──────────────────────────────────────────────
class SignupSmsRequest(BaseModel):
    phone: str = Field(..., examples=["+26934125678"])
    role: UserRole = UserRole.STUDENT
    locale: str = "fr-KM"
    grade_level: str | None = None
    device_id: str | None = None

    _phone_validator = field_validator("phone")(_validate_phone)


class SignupSmsResponse(BaseModel):
    challenge_id: uuid.UUID
    phone: str
    expires_in_seconds: int
    message: str = "Un code à 6 chiffres a été envoyé par SMS."


# ──────────────────────────────────────────────
#  Verify OTP (1ère inscription OU login)
# ──────────────────────────────────────────────
class VerifyOtpRequest(BaseModel):
    phone: str
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    device_id: str | None = None

    _phone_validator = field_validator("phone")(_validate_phone)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["Bearer"] = "Bearer"
    expires_in: int


class UserPublic(BaseModel):
    id: uuid.UUID
    phone: str
    role: UserRole
    locale: str
    full_name: str | None = None
    grade_level: str | None = None
    account_state: AccountState


class SignupVerifyResponse(BaseModel):
    user: UserPublic
    token: TokenResponse
    free_trial_scans: int = 3
    free_trial_expires_at: datetime
    message: str = "Bienvenue ! 3 scans gratuits valables 7 jours."


# ──────────────────────────────────────────────
#  Login (vendor ticket OR last valid OTP en grace)
# ──────────────────────────────────────────────
class LoginRequest(BaseModel):
    phone: str
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    device_id: str | None = None

    _phone_validator = field_validator("phone")(_validate_phone)


class LoginResponseActive(BaseModel):
    state: Literal["active"] = "active"
    user: UserPublic
    token: TokenResponse
    credit: dict


class LoginResponseGrace(BaseModel):
    state: Literal["grace"] = "grace"
    user: UserPublic
    token: TokenResponse
    days_remaining_grace: int
    credit_expired_at: datetime
    message: str
    paywall: bool = True


class LoginResponseFrozen(BaseModel):
    state: Literal["frozen"] = "frozen"
    error: Literal["account_frozen"] = "account_frozen"
    message: str
    data_export_url: str


# ──────────────────────────────────────────────
#  Me — account state / credit status
# ──────────────────────────────────────────────
class AccountStateResponse(BaseModel):
    state: AccountState
    credit_expires_at: datetime | None = None
    days_remaining_grace: int | None = None
    days_until_freeze: int | None = None
    can_perform_new_actions: bool
    paywall_required: bool


class CreditStatusResponse(BaseModel):
    remaining_scans: int
    plan: str
    expires_at: datetime | None = None
    days_until_expiry: int | None = None
    is_active: bool
