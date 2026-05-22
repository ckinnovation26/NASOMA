"""Endpoints Spaced Repetition (révisions espacées)."""

from __future__ import annotations

import uuid
from datetime import date

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.spaced_repetition_service import SpacedRepetitionService

logger = structlog.get_logger(__name__)

router = APIRouter()


class DueReviewItem(BaseModel):
    review_id: uuid.UUID
    concept_code: str
    concept_name: str
    interval_days: int
    scheduled_for: date


class DueReviewsResponse(BaseModel):
    for_date: date
    count: int
    reviews: list[DueReviewItem]


class CompleteReviewPayload(BaseModel):
    student_id: uuid.UUID
    correct: bool


class CompleteReviewResponse(BaseModel):
    review_id: uuid.UUID
    status: str
    outcome: str | None
    mastery_before: float | None
    mastery_after: float | None
    interval_days: int


@router.get(
    "/students/{student_id}/reviews/due",
    response_model=DueReviewsResponse,
    summary="Reviews espacées dues aujourd'hui (Moat #6)",
)
async def get_due_reviews(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> DueReviewsResponse:
    svc = SpacedRepetitionService(db)
    pairs = await svc.get_due_today(student_id)
    items = [
        DueReviewItem(
            review_id=r.id,
            concept_code=c.code,
            concept_name=c.name,
            interval_days=r.interval_days,
            scheduled_for=r.scheduled_for,
        )
        for r, c in pairs
    ]
    return DueReviewsResponse(
        for_date=date.today(),
        count=len(items),
        reviews=items,
    )


@router.post(
    "/reviews/{review_id}/complete",
    response_model=CompleteReviewResponse,
    summary="Soumettre le résultat d'une review espacée",
)
async def complete_review(
    review_id: uuid.UUID,
    payload: CompleteReviewPayload,
    db: AsyncSession = Depends(get_db),
) -> CompleteReviewResponse:
    svc = SpacedRepetitionService(db)
    try:
        result = await svc.complete_review(
            review_id=review_id,
            student_id=payload.student_id,
            correct=payload.correct,
        )
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e

    await db.commit()
    return CompleteReviewResponse(
        review_id=uuid.UUID(result["review_id"]),
        status=result["status"],
        outcome=result["outcome"],
        mastery_before=result["mastery_before"],
        mastery_after=result["mastery_after"],
        interval_days=result["interval_days"],
    )


@router.post(
    "/internal/reviews/auto-schedule",
    summary="[CRON] Auto-schedule SR pour tous les concepts maîtrisés sans review",
)
async def auto_schedule(
    db: AsyncSession = Depends(get_db),
) -> dict:
    svc = SpacedRepetitionService(db)
    count = await svc.auto_schedule_for_newly_mastered()
    return {"concepts_newly_scheduled": count}
