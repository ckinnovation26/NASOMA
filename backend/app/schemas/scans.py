"""Schémas Pydantic — endpoints scans."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ScanCreateRequest(BaseModel):
    """Métadonnées accompagnant l'upload d'une image scan."""

    student_id: uuid.UUID
    subject_code: Literal["MATH", "FR", "AR", "SCI"] = "MATH"
    grade_level: Literal["CM1", "CM2", "6E"] | None = None
    mlkit_text: str | None = None
    mlkit_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    device_id: str | None = None


class DiagnosticPublic(BaseModel):
    id: uuid.UUID
    detected_errors: list
    summary_text: str | None
    total_exercises_detected: int
    correct_count: int
    incorrect_count: int


class ScanCreateResponse(BaseModel):
    """Réponse à POST /scans — BACKEND = DÉTECTION, APP = DÉCISION UX.

    Le champ `detection_type` permet à l'app de décider quel flow proposer :
    - SUCCESS → afficher diagnostic + session
    - IMAGE_QUALITY_LOW / HANDWRITING_ILLEGIBLE / etc. → l'app décide :
        - 1ère fois : afficher bouton "Reprendre"
        - 2ème fois : ouvrir modal contexte parent
        - Si récurrence : proposer assistance
    """

    scan_id: uuid.UUID
    status: str
    detection_type: str
    detection_details: dict | None = None
    diagnostic_id: uuid.UUID | None = None
    session_id: uuid.UUID | None = None
    cached_from_phash: bool = False
    ocr_confidence: float | None = None
    summary_text: str
    quota_remaining_after: int


class ScanDetailResponse(BaseModel):
    scan_id: uuid.UUID
    status: str
    detection_type: str | None = None
    ocr_provider: str | None = None
    ocr_confidence: float | None = None
    fallback_used: bool
    fallback_reason: str | None = None
    diagnostic: DiagnosticPublic | None = None
    session_id: uuid.UUID | None = None
    created_at: datetime
    processed_at: datetime | None = None
