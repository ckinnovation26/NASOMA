"""Endpoints indicateurs CT/MT/LT — cœur de valeur Nasoma."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.indicators import IndicatorHorizon
from app.schemas.indicators import (
    DailyAction,
    DailyRecommendationsResponse,
    IndicatorResponse,
    RecommendationItem,
    TrajectoryPoint,
    TrajectoryResponse,
)
from app.services.indicators_service import IndicatorsService

logger = structlog.get_logger(__name__)

router = APIRouter()


# ──────────────────────────────────────────────
#  GET /students/{id}/indicators?horizon=ct|mt|lt
# ──────────────────────────────────────────────
@router.get(
    "/students/{student_id}/indicators",
    response_model=IndicatorResponse,
    summary="Indicateur CT, MT ou LT — trajectoire d'apprentissage",
)
async def get_indicator(
    student_id: uuid.UUID,
    horizon: IndicatorHorizon = Query(..., description="ct | mt | lt"),
    db: AsyncSession = Depends(get_db),
) -> IndicatorResponse:
    """Retourne le dernier indicateur calculé pour l'horizon choisi.

    Si pas encore calculé, déclenche un calcul à la volée (premier accès).
    """
    svc = IndicatorsService(db)
    indicator = await svc.get_latest(student_id, horizon)

    if indicator is None:
        # Premier accès — calcul à la volée
        from app.models.users import User

        user = await db.get(User, student_id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Élève introuvable.")
        await svc.compute_indicators_for_student(student_id, user.tenant_id)
        await db.commit()
        indicator = await svc.get_latest(student_id, horizon)
        if indicator is None:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Indicateur introuvable après calcul.",
            )

    horizon_str = (
        indicator.horizon.value
        if hasattr(indicator.horizon, "value")
        else str(indicator.horizon)
    )

    return IndicatorResponse(
        horizon=horizon_str,  # type: ignore[arg-type]
        period_start=indicator.period_start,
        period_end=indicator.period_end,
        metrics=indicator.metrics,
        recommendations=[
            RecommendationItem(**r) for r in (indicator.recommendations or [])
        ],
        computed_at=indicator.computed_at,
        as_of=datetime.now(UTC),
    )


# ──────────────────────────────────────────────
#  GET /students/{id}/trajectory
# ──────────────────────────────────────────────
@router.get(
    "/students/{student_id}/trajectory",
    response_model=TrajectoryResponse,
    summary="Série temporelle BKT pour graphique",
)
async def get_trajectory(
    student_id: uuid.UUID,
    subject: str | None = Query(None, description="Filtre par matière (MATH/FR/AR/SCI)"),
    days: int = Query(90, ge=7, le=730),
    db: AsyncSession = Depends(get_db),
) -> TrajectoryResponse:
    svc = IndicatorsService(db)
    points = await svc.get_trajectory(student_id, subject_code=subject, days=days)
    return TrajectoryResponse(
        student_id=student_id,
        subject_filter=subject,
        days=days,
        points=[TrajectoryPoint(**p) for p in points],
    )


# ──────────────────────────────────────────────
#  GET /students/{id}/recommendations/daily
# ──────────────────────────────────────────────
@router.get(
    "/students/{student_id}/recommendations/daily",
    response_model=DailyRecommendationsResponse,
    summary="Actions recommandées pour J+1",
)
async def get_daily_recommendations(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> DailyRecommendationsResponse:
    svc = IndicatorsService(db)
    raw = await svc.get_daily_recommendations(student_id)

    actions: list[DailyAction] = []
    for r in raw:
        actions.append(
            DailyAction(
                type="exercise" if r.get("action") == "exercise_session" else "general",
                target_concept_code=r.get("target_concept_code"),
                duration_minutes=r.get("duration_minutes"),
                best_time_hint="soir avant les devoirs",
                rationale=r.get("rationale", ""),
            )
        )

    parent_summary = (
        f"{len(actions)} action(s) recommandée(s) pour demain."
        if actions
        else "Aucune action ciblée — continue à pratiquer régulièrement."
    )

    return DailyRecommendationsResponse(
        for_date=date.today(),
        actions=actions,
        parent_summary=parent_summary,
    )


# ──────────────────────────────────────────────
#  POST /internal/indicators/compute (cron)
# ──────────────────────────────────────────────
@router.post(
    "/internal/indicators/compute",
    summary="[CRON] Recalcule snapshots + indicateurs pour tous les actifs",
)
async def compute_batch(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Cron quotidien — appelé par Cloud Scheduler à 02:00 locale.

    1. Capture snapshot BKT du jour
    2. Recalcule les indicateurs CT/MT/LT pour tous les comptes ACTIVE
    """
    svc = IndicatorsService(db)
    snapshots = await svc.compute_daily_snapshots()
    computed = await svc.compute_for_all_active_students()
    return {
        "snapshots_captured": snapshots,
        "students_computed": computed,
        "computed_at": datetime.now(UTC).isoformat(),
    }
