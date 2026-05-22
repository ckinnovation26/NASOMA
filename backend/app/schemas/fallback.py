"""Schémas Pydantic — endpoints fallback context + assistance."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.fallback import AssistanceReason, AssistanceStatus


class RetryScanRequest(BaseModel):
    """L'utilisateur veut retenter un scan illisible (gratuit dans les 5 min)."""

    student_id: uuid.UUID


class RetryScanResponse(BaseModel):
    new_scan_id: uuid.UUID
    is_free_retry: bool
    retry_count: int


class FallbackContextRequest(BaseModel):
    """Modal contexte parent après retry illisible."""

    subject_code: Literal["MATH", "FR", "AR", "SCI"]
    grade_level: Literal["CM1", "CM2", "6E"]
    recent_grade: float | None = Field(default=None, ge=0.0, le=20.0)
    max_grade: float | None = Field(default=20.0, ge=1.0, le=100.0)
    parent_comment: str | None = Field(default=None, max_length=500)


class FallbackContextResponse(BaseModel):
    context_id: uuid.UUID
    session_id: uuid.UUID
    exercises_count: int
    summary_text: str
    show_assistance_prompt: bool = False


class AssistanceRequestPayload(BaseModel):
    """Demande d'assistance — GPS user optionnel pour recommander vendeur proche."""

    reason: AssistanceReason
    user_latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    user_longitude: float | None = Field(default=None, ge=-180.0, le=180.0)


class VendorRecommendationPublic(BaseModel):
    vendor_id: uuid.UUID
    code: str
    name: str
    contact_phone: str
    distance_km: float | None = None
    source: Literal["ticket_vendor", "nearest_gps", "fallback_any"]
    is_trained_level1: bool


class AssistanceRequestResponse(BaseModel):
    request_id: uuid.UUID
    status: AssistanceStatus
    primary_vendor: VendorRecommendationPublic | None
    alternative_vendor: VendorRecommendationPublic | None = None
    courtesy_rescan_granted: bool
    message: str
    estimated_callback_hours: int = 24


class ScanQualityStatsResponse(BaseModel):
    failed_scans_last_7d: int
    threshold_for_assistance: int = 3
    assistance_should_be_offered: bool
    last_assistance_request_at: datetime | None = None
