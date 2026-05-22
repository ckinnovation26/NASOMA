"""Endpoints fallback — retry scan + contexte parent + assistance vendeur."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.fallback import (
    AssistanceReason,
    AssistanceStatus,
    FallbackContext,
    VendorAssistanceRequest,
)
from app.models.scans import Scan, ScanStatus
from app.models.sessions import Session, SessionStatus
from app.models.tenants import Tenant
from app.schemas.fallback import (
    AssistanceRequestPayload,
    AssistanceRequestResponse,
    FallbackContextRequest,
    FallbackContextResponse,
    ScanQualityStatsResponse,
)
from app.services.exercise_generator_service import ExerciseGeneratorService
from app.services.scan_quality_service import ScanQualityService

logger = structlog.get_logger(__name__)

router = APIRouter()


async def _default_tenant_id(db: AsyncSession) -> uuid.UUID:
    result = await db.execute(select(Tenant.id).where(Tenant.code == "KM"))
    tenant_id = result.scalar_one_or_none()
    if tenant_id is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Tenant KM introuvable.")
    return tenant_id


# ──────────────────────────────────────────────
#  POST /scans/{id}/retry — étape 1 du fallback (gratuit dans grace window)
# ──────────────────────────────────────────────
@router.post(
    "/scans/{scan_id}/retry",
    summary="Indiquer qu'on va retenter — réserve le slot gratuit dans les 5 min",
)
async def initiate_retry(
    scan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Marque le scan original comme "en attente de retry" et autorise un re-scan gratuit
    dans la fenêtre `FALLBACK_RESCAN_GRACE_MINUTES`.

    Le client doit ensuite faire un POST /scans normal avec `retry_of_scan_id={scan_id}`
    dans le payload pour matérialiser le retry.
    """
    original_scan = await db.get(Scan, scan_id)
    if original_scan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Scan introuvable.")

    if original_scan.status not in (ScanStatus.DONE_WITH_FALLBACK, ScanStatus.PROCESSING):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Seuls les scans en fallback peuvent être retentés.",
        )

    grace_minutes = settings.fallback_rescan_grace_minutes
    elapsed = datetime.now(UTC) - original_scan.created_at.replace(tzinfo=UTC)
    if elapsed > timedelta(minutes=grace_minutes):
        raise HTTPException(
            status.HTTP_410_GONE,
            f"Délai de retry gratuit ({grace_minutes} min) dépassé.",
        )

    return {
        "original_scan_id": str(scan_id),
        "free_retry_until": (
            original_scan.created_at + timedelta(minutes=grace_minutes)
        ).isoformat(),
        "instructions": (
            f"Reprends la photo dans les {grace_minutes} minutes. "
            "Soumets ensuite POST /scans avec retry_of_scan_id."
        ),
    }


# ──────────────────────────────────────────────
#  POST /scans/{id}/fallback-context — étape 2 du fallback (modal parent)
# ──────────────────────────────────────────────
@router.post(
    "/scans/{scan_id}/fallback-context",
    response_model=FallbackContextResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Soumettre le contexte parent après retry illisible — génère exos ciblés",
)
async def submit_fallback_context(
    scan_id: uuid.UUID,
    payload: FallbackContextRequest,
    db: AsyncSession = Depends(get_db),
) -> FallbackContextResponse:
    """L'étape 2 du flow refiné — modal contexte après retry illisible.

    Le parent a fourni :
    - matière (confirmée)
    - grade_level (confirmé/modifié)
    - note récente (indice de difficulté)
    - commentaire libre sur le sujet du devoir
    """
    scan = await db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Scan introuvable.")
    if scan.status != ScanStatus.DONE_WITH_FALLBACK:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Le scan n'est pas en fallback — contexte non applicable.",
        )

    tenant_id = await _default_tenant_id(db)

    # Persister le contexte
    quality = ScanQualityService(db)
    context = FallbackContext(
        tenant_id=tenant_id,
        scan_id=scan_id,
        student_id=scan.student_id,
        subject_code=payload.subject_code,
        grade_level=payload.grade_level,
        recent_grade=payload.recent_grade,
        max_grade=payload.max_grade,
        parent_comment=payload.parent_comment,
        extracted_keywords=quality.extract_keywords(payload.parent_comment),
    )
    db.add(context)
    await db.flush()

    # Générer des exos contextualisés
    generator = ExerciseGeneratorService(db)
    # Heuristique : si note basse (< 10/20), cibler les fondamentaux
    targeting_hint_low = (
        payload.recent_grade is not None
        and payload.max_grade
        and (payload.recent_grade / payload.max_grade) < 0.5
    )
    templates = await generator.generate_fallback_for_student(
        student_id=scan.student_id,
        tenant_id=tenant_id,
        grade_level=payload.grade_level,
        subject_code=payload.subject_code,
    )

    if not templates:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Pas d'exercices fallback disponibles (KG vide pour ce niveau/matière).",
        )

    # Créer la session fallback
    session = Session(
        tenant_id=tenant_id,
        student_id=scan.student_id,
        target_concept_id=templates[0].concept_id,
        status=SessionStatus.IN_PROGRESS,
        exercise_order=[str(t.id) for t in templates],
    )
    db.add(session)
    await db.flush()

    # Doit-on proposer l'assistance vendeur (récurrence) ?
    show_assistance = await quality.should_propose_assistance(scan.student_id)

    await db.commit()

    summary = (
        f"Exercices ciblés sur {payload.subject_code} {payload.grade_level}"
        + (" (focus fondamentaux)" if targeting_hint_low else "")
        + (
            f" — basés sur le commentaire : « {payload.parent_comment[:60]}... »"
            if payload.parent_comment
            else ""
        )
    )

    return FallbackContextResponse(
        context_id=context.id,
        session_id=session.id,
        exercises_count=len(templates),
        summary_text=summary,
        show_assistance_prompt=show_assistance,
    )


# ──────────────────────────────────────────────
#  POST /assistance/request — étape 3 du fallback (récurrence)
# ──────────────────────────────────────────────
@router.post(
    "/assistance/request",
    response_model=AssistanceRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Demande d'assistance vendeur (récurrence ≥ 3 scans illisibles en 7j)",
)
async def request_assistance(
    student_id: uuid.UUID,
    payload: AssistanceRequestPayload,
    db: AsyncSession = Depends(get_db),
) -> AssistanceRequestResponse:
    """Crée une demande d'assistance vendeur."""
    tenant_id = await _default_tenant_id(db)
    quality = ScanQualityService(db)

    # Si l'utilisateur dit "c'est vraiment le devoir illisible", on ne crée pas
    # d'assistance vendeur mais on log pour BI
    if payload.reason == AssistanceReason.HOMEWORK_REALLY_ILLEGIBLE:
        logger.info(
            "assistance.declined_user_blames_homework",
            student=str(student_id),
        )
        # On crée quand même un record pour respecter le cooldown 7j
        request = await quality.create_assistance_request(
            user_id=student_id,
            tenant_id=tenant_id,
            reason=payload.reason,
        )
        request.status = AssistanceStatus.DECLINED
        await db.commit()
        return AssistanceRequestResponse(
            request_id=request.id,
            status=AssistanceStatus.DECLINED,
            primary_vendor=None,
            alternative_vendor=None,
            courtesy_rescan_granted=False,
            message="Pas de souci — continuons avec les exos ciblés sur le profil.",
        )

    # Cas Camera défective ou Photo skill : créer assistance + courtesy rescan
    request = await quality.create_assistance_request(
        user_id=student_id,
        tenant_id=tenant_id,
        reason=payload.reason,
    )
    request.courtesy_rescan_granted = True
    request.status = AssistanceStatus.NOTIFIED
    request.notified_at = datetime.now(UTC)

    # ─── Recommandation vendeur (ticket d'abord, sinon GPS proche) ───
    from app.schemas.fallback import VendorRecommendationPublic
    from app.services.vendor_service import VendorService

    vendor_svc = VendorService(db)
    primary_reco = await vendor_svc.recommend_for_assistance(
        user_id=student_id,
        user_latitude=payload.user_latitude,
        user_longitude=payload.user_longitude,
    )

    # On essaie aussi de proposer une alternative (le vendeur du ticket si on a choisi GPS)
    alternative_reco = None
    if primary_reco and primary_reco.source == "nearest_gps":
        # Le ticket vendor existe-t-il en tant que vendeur ?
        ticket_vendor = await vendor_svc.get_ticket_vendor(student_id)
        if ticket_vendor:
            from app.services.vendor_service import haversine_km

            distance = None
            if (
                payload.user_latitude is not None
                and payload.user_longitude is not None
                and ticket_vendor.latitude is not None
                and ticket_vendor.longitude is not None
            ):
                distance = haversine_km(
                    payload.user_latitude,
                    payload.user_longitude,
                    ticket_vendor.latitude,
                    ticket_vendor.longitude,
                )
            alternative_reco = VendorRecommendationPublic(
                vendor_id=ticket_vendor.id,
                code=ticket_vendor.code,
                name=ticket_vendor.name,
                contact_phone=ticket_vendor.contact_phone,
                distance_km=distance,
                source="ticket_vendor",
                is_trained_level1=ticket_vendor.is_trained_level1,
            )

    await db.commit()

    msg_by_reason = {
        AssistanceReason.CAMERA_DEFECTIVE: (
            "Compris — un vendeur Nasoma va te contacter pour vérifier "
            "l'objectif de ton téléphone. Un re-scan gratuit t'est offert aujourd'hui."
        ),
        AssistanceReason.PHOTO_TAKING_SKILL: (
            "On va te montrer comment bien prendre les photos. "
            "Un vendeur local te contactera, et tu as droit à un re-scan gratuit aujourd'hui."
        ),
    }

    primary_public = None
    if primary_reco:
        primary_public = VendorRecommendationPublic(
            vendor_id=primary_reco.vendor_id,
            code=primary_reco.code,
            name=primary_reco.name,
            contact_phone=primary_reco.contact_phone,
            distance_km=primary_reco.distance_km,
            source=primary_reco.source,
            is_trained_level1=primary_reco.is_trained_level1,
        )

    return AssistanceRequestResponse(
        request_id=request.id,
        status=AssistanceStatus.NOTIFIED,
        primary_vendor=primary_public,
        alternative_vendor=alternative_reco,
        courtesy_rescan_granted=True,
        message=msg_by_reason.get(
            payload.reason, "Demande d'assistance enregistrée."
        ),
    )


# ──────────────────────────────────────────────
#  GET /me/scan-quality-stats
# ──────────────────────────────────────────────
@router.get(
    "/me/scan-quality-stats",
    response_model=ScanQualityStatsResponse,
    summary="Stats qualité scans — pour déclencher l'assistance UI",
)
async def get_scan_quality_stats(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ScanQualityStatsResponse:
    quality = ScanQualityService(db)
    failed_count = await quality.count_failed_scans_last_7d(student_id)
    should_offer = await quality.should_propose_assistance(student_id)

    # Dernière demande assistance
    stmt = (
        select(VendorAssistanceRequest.created_at)
        .where(VendorAssistanceRequest.user_id == student_id)
        .order_by(VendorAssistanceRequest.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    last_request = result.scalar_one_or_none()

    return ScanQualityStatsResponse(
        failed_scans_last_7d=failed_count,
        assistance_should_be_offered=should_offer,
        last_assistance_request_at=last_request,
    )
