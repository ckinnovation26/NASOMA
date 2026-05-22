"""Endpoints sessions — récupération exos + soumission réponses + complétion."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.concepts import Concept
from app.models.sessions import (
    ExerciseTemplate,
    Session,
    SessionAnswer,
    SessionStatus,
)
from app.schemas.sessions import (
    CompleteSessionResponse,
    ExercisePublic,
    SessionDetailResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.services.bkt_service import BktService, status_for

logger = structlog.get_logger(__name__)

router = APIRouter()


# ──────────────────────────────────────────────
#  GET /sessions/{id}
# ──────────────────────────────────────────────
@router.get(
    "/{session_id}",
    response_model=SessionDetailResponse,
    summary="Récupère le pack d'exercices d'une session",
)
async def get_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> SessionDetailResponse:
    session = await db.get(Session, session_id)
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session introuvable.")

    target_concept = await db.get(Concept, session.target_concept_id)

    # Charger les templates dans l'ordre
    order_ids = [uuid.UUID(s) for s in (session.exercise_order or [])]
    if not order_ids:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Session sans ordre d'exercices.",
        )

    stmt = select(ExerciseTemplate).where(ExerciseTemplate.id.in_(order_ids))
    result = await db.execute(stmt)
    templates_by_id = {t.id: t for t in result.scalars().all()}

    exercises: list[ExercisePublic] = []
    for i, tid in enumerate(order_ids):
        t = templates_by_id.get(tid)
        if t is None:
            continue
        tj = t.template_json
        exercises.append(
            ExercisePublic(
                id=t.id,
                type=t.type.value if hasattr(t.type, "value") else str(t.type),
                prompt=tj.get("prompt", ""),
                options=tj.get("options"),
                tts_text=tj.get("tts_text"),
                order=tj.get("order", i),
            )
        )

    # Progress
    answers_stmt = select(SessionAnswer).where(SessionAnswer.session_id == session_id)
    answers_result = await db.execute(answers_stmt)
    answers = answers_result.scalars().all()
    answered_count = len(answers)
    correct_count = sum(1 for a in answers if a.is_correct)

    return SessionDetailResponse(
        session_id=session.id,
        target_concept_code=target_concept.code if target_concept else "UNKNOWN",
        target_concept_name=target_concept.name if target_concept else "",
        status=session.status.value if hasattr(session.status, "value") else str(session.status),
        exercises=exercises,
        progress={
            "answered_count": answered_count,
            "total_count": len(exercises),
            "correct_count": correct_count,
        },
    )


# ──────────────────────────────────────────────
#  POST /sessions/{id}/answers
# ──────────────────────────────────────────────
@router.post(
    "/{session_id}/answers",
    response_model=SubmitAnswerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Soumettre une réponse — déclenche update BKT",
)
async def submit_answer(
    session_id: uuid.UUID,
    payload: SubmitAnswerRequest,
    db: AsyncSession = Depends(get_db),
) -> SubmitAnswerResponse:
    session = await db.get(Session, session_id)
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session introuvable.")
    if session.status == SessionStatus.COMPLETED:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Session déjà terminée.")

    template = await db.get(ExerciseTemplate, payload.exercise_template_id)
    if template is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Exercice introuvable.")

    # Vérifier la réponse
    expected = template.template_json.get("answer")
    is_correct = str(payload.answer).strip().lower() == str(expected).strip().lower()
    explanation = template.template_json.get("explanation_short")

    # Update BKT
    bkt = BktService(db)
    update_result = await bkt.record_answer(
        student_id=session.student_id,
        concept_id=template.concept_id,
        tenant_id=session.tenant_id,
        correct=is_correct,
    )

    # Persister la réponse
    answer = SessionAnswer(
        session_id=session_id,
        exercise_template_id=template.id,
        student_answer=payload.answer,
        is_correct=is_correct,
        response_time_ms=payload.response_time_ms,
        mastery_before=update_result.mastery_before,
        mastery_after=update_result.mastery_after,
    )
    db.add(answer)
    await db.commit()

    return SubmitAnswerResponse(
        correct=is_correct,
        explanation=explanation,
        mastery_before=update_result.mastery_before,
        mastery_after=update_result.mastery_after,
        mastery_status=update_result.status_after,
        became_mastered=update_result.became_mastered,
        became_blocked=update_result.became_blocked,
    )


# ──────────────────────────────────────────────
#  POST /sessions/{id}/complete
# ──────────────────────────────────────────────
@router.post(
    "/{session_id}/complete",
    response_model=CompleteSessionResponse,
    summary="Terminer une session — calcule success_rate et propose next concept",
)
async def complete_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CompleteSessionResponse:
    session = await db.get(Session, session_id)
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session introuvable.")
    if session.status == SessionStatus.COMPLETED:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Session déjà terminée.")

    # Récupérer les réponses
    stmt = select(SessionAnswer).where(SessionAnswer.session_id == session_id)
    result = await db.execute(stmt)
    answers = result.scalars().all()

    if not answers:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Aucune réponse soumise — impossible de compléter.",
        )

    correct_count = sum(1 for a in answers if a.is_correct)
    success_rate = correct_count / len(answers)
    is_passed = success_rate > 0.75      # R11 BP — séance validée si > 75 %

    # Récupérer le concept cible + mastery actuelle
    target_concept = await db.get(Concept, session.target_concept_id)
    bkt = BktService(db)
    mastery = await bkt.get_or_create(
        session.student_id, session.target_concept_id, session.tenant_id
    )

    # Suggérer le concept suivant si maîtrisé
    next_concept_code = None
    if mastery.mastery_probability >= 0.85 and target_concept:
        # Cherche un concept dépendant (qui requiert ce concept comme prérequis)
        # Simplifié pour Sprint 2 — Sprint 2.5 = parcours du DAG
        from app.models.concepts import ConceptPrerequisite

        stmt_next = (
            select(Concept)
            .join(
                ConceptPrerequisite,
                ConceptPrerequisite.concept_id == Concept.id,
            )
            .where(ConceptPrerequisite.prereq_id == session.target_concept_id)
            .limit(1)
        )
        next_result = await db.execute(stmt_next)
        next_concept = next_result.scalar_one_or_none()
        if next_concept:
            next_concept_code = next_concept.code

    # Marquer la session complétée
    session.status = SessionStatus.COMPLETED
    session.completed_at = datetime.now(UTC)
    session.success_rate = success_rate
    await db.commit()

    logger.info(
        "session.completed",
        session_id=str(session_id),
        success_rate=round(success_rate, 2),
        is_passed=is_passed,
    )

    return CompleteSessionResponse(
        session_id=session_id,
        success_rate=success_rate,
        is_passed=is_passed,
        target_concept_code=target_concept.code if target_concept else "UNKNOWN",
        concept_mastery_after=mastery.mastery_probability,
        next_concept_suggested_code=next_concept_code,
        completed_at=session.completed_at,
    )
