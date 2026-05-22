"""Schémas Pydantic — endpoints sessions."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ExercisePublic(BaseModel):
    """Vue publique d'un exercice (sans la réponse correcte)."""

    id: uuid.UUID
    type: Literal["mcq", "fill_blank", "short_text", "drag_drop"]
    prompt: str
    options: list[str] | None = None
    tts_text: str | None = None
    order: int


class SessionDetailResponse(BaseModel):
    session_id: uuid.UUID
    target_concept_code: str
    target_concept_name: str
    status: str
    exercises: list[ExercisePublic]
    progress: dict


class SubmitAnswerRequest(BaseModel):
    exercise_template_id: uuid.UUID
    answer: str = Field(..., max_length=500)
    response_time_ms: int | None = Field(default=None, ge=0)


class SubmitAnswerResponse(BaseModel):
    correct: bool
    explanation: str | None
    mastery_before: float
    mastery_after: float
    mastery_status: str            # 'maitrise' | 'en_cours' | 'non_maitrise'
    became_mastered: bool
    became_blocked: bool


class CompleteSessionResponse(BaseModel):
    session_id: uuid.UUID
    success_rate: float
    is_passed: bool                # > 75 % (cf. R11 BP)
    target_concept_code: str
    concept_mastery_after: float
    next_concept_suggested_code: str | None
    completed_at: datetime
