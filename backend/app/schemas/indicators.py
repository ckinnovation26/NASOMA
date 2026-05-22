"""Schémas Pydantic — endpoints indicateurs CT/MT/LT."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


class RecommendationItem(BaseModel):
    action: str
    target_concept_code: str | None = None
    target_subject: str | None = None
    target: str | None = None
    rationale: str
    duration_minutes: int | None = None
    minutes_per_day: int | None = None
    priority: Literal["low", "medium", "high"] | None = None


class IndicatorResponse(BaseModel):
    horizon: Literal["ct", "mt", "lt"]
    period_start: date
    period_end: date
    metrics: dict
    recommendations: list[RecommendationItem]
    computed_at: datetime
    as_of: datetime


class TrajectoryPoint(BaseModel):
    date: str
    mastery_avg: float


class TrajectoryResponse(BaseModel):
    student_id: uuid.UUID
    subject_filter: str | None
    days: int
    points: list[TrajectoryPoint]


class DailyAction(BaseModel):
    type: Literal["exercise", "review", "milestone", "general"]
    target_concept_code: str | None = None
    duration_minutes: int | None = None
    best_time_hint: str | None = None
    rationale: str


class DailyRecommendationsResponse(BaseModel):
    for_date: date
    actions: list[DailyAction]
    parent_summary: str
