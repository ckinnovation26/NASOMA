"""Schémas Pydantic — endpoints paiements."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class PaymentInitiatePayload(BaseModel):
    user_id: uuid.UUID
    plan: Literal["daily", "three_day", "weekly", "monthly"]
    provider: Literal["hollo", "mvola", "stripe", "physical_ticket"]
    vendor_code: str | None = None
    school_id: uuid.UUID | None = None


class PaymentInitiateResponse(BaseModel):
    payment_id: uuid.UUID
    provider_ref: str
    user_action_text: str | None = None
    ussd_code: str | None = None
    redirect_url: str | None = None
    expires_in_seconds: int


class PaymentDetailResponse(BaseModel):
    payment_id: uuid.UUID
    status: str
    amount_local: float
    currency: str
    provider: str
    provider_ref: str | None
    created_at: datetime
    completed_at: datetime | None
