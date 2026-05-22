"""Endpoints scans — upload + récupération diagnostic."""

from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.scans import Scan
from app.models.tenants import Tenant
from app.schemas.scans import DiagnosticPublic, ScanCreateResponse, ScanDetailResponse
from app.services.quota_service import (
    QuotaExhaustedError,
    QuotaExpiredError,
    QuotaThrottledError,
)
from app.services.scan_processor_service import ScanProcessorService

logger = structlog.get_logger(__name__)

router = APIRouter()


async def _default_tenant_id(db: AsyncSession) -> uuid.UUID:
    """Récupère le tenant 'KM' (seul tenant MVP)."""
    result = await db.execute(select(Tenant.id).where(Tenant.code == "KM"))
    tenant_id = result.scalar_one_or_none()
    if tenant_id is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Tenant KM introuvable."
        )
    return tenant_id


# ──────────────────────────────────────────────
#  POST /scans
# ──────────────────────────────────────────────
@router.post(
    "",
    response_model=ScanCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Uploader une image et lancer le pipeline OCR + diagnostic + exos",
)
async def create_scan(
    student_id: uuid.UUID = Form(...),
    subject_code: str = Form("MATH"),
    grade_level: str | None = Form(None),
    mlkit_text: str | None = Form(None),
    mlkit_confidence: float | None = Form(None),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> ScanCreateResponse:
    """Upload une image et déclenche le pipeline complet.

    Workflow :
    1. Vérifier la taille (< 200 KB)
    2. pHash check (cache 24h, pas de décrément quota)
    3. Décrémenter quota Firestore atomique
    4. OCR pipeline 3 étages
    5. Mapping concept + génération exos
    6. Si échec OCR → fallback exos depuis profil BKT (Always Give Value)
    7. Archiver dans corpus (Moat #1)
    """
    image_bytes = await image.read()

    # Validation taille
    max_kb = settings.quota_max_upload_size_kb
    if len(image_bytes) > max_kb * 1024:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"Image trop grande ({len(image_bytes) // 1024} KB > {max_kb} KB)",
        )

    tenant_id = await _default_tenant_id(db)

    # TODO Sprint 2.5 : upload réel dans Cloud Storage
    # Pour Sprint 2, on simule un storage_key
    storage_key = f"scans/{student_id}/{uuid.uuid4()}.jpg"

    processor = ScanProcessorService(db)
    try:
        result = await processor.process(
            student_id=student_id,
            tenant_id=tenant_id,
            image_bytes=image_bytes,
            image_storage_key=storage_key,
            subject_code=subject_code,
            grade_level=grade_level,
            mlkit_text=mlkit_text,
            mlkit_confidence=mlkit_confidence,
        )
    except QuotaExhaustedError as e:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, str(e)) from e
    except QuotaThrottledError as e:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, str(e)) from e
    except QuotaExpiredError as e:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, str(e)) from e

    await db.commit()

    logger.info(
        "scan.created",
        scan_id=str(result.scan_id),
        student=str(student_id),
        status=result.status,
        fallback=result.fallback_used,
    )

    return ScanCreateResponse(
        scan_id=result.scan_id,
        status=result.status.value
        if hasattr(result.status, "value")
        else str(result.status),
        detection_type=result.detection_type.value
        if hasattr(result.detection_type, "value")
        else str(result.detection_type),
        detection_details=result.detection_details,
        diagnostic_id=result.diagnostic_id,
        session_id=result.session_id,
        cached_from_phash=result.cached_from_phash,
        ocr_confidence=result.ocr_confidence,
        summary_text=result.summary_text,
        quota_remaining_after=result.quota_remaining_after,
    )


# ──────────────────────────────────────────────
#  GET /scans/{id}
# ──────────────────────────────────────────────
@router.get(
    "/{scan_id}",
    response_model=ScanDetailResponse,
    summary="Détail d'un scan + diagnostic",
)
async def get_scan(
    scan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ScanDetailResponse:
    scan = await db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Scan introuvable.")

    # Charger relation diagnostic
    await db.refresh(scan, attribute_names=["diagnostic"])

    diagnostic_payload = None
    session_id = None
    if scan.diagnostic:
        diagnostic_payload = DiagnosticPublic(
            id=scan.diagnostic.id,
            detected_errors=scan.diagnostic.detected_errors,
            summary_text=scan.diagnostic.summary_text,
            total_exercises_detected=scan.diagnostic.total_exercises_detected,
            correct_count=scan.diagnostic.correct_count,
            incorrect_count=scan.diagnostic.incorrect_count,
        )
        # Récupérer la session associée
        from app.models.sessions import Session

        result = await db.execute(
            select(Session.id).where(Session.diagnostic_id == scan.diagnostic.id)
        )
        session_id = result.scalar_one_or_none()

    return ScanDetailResponse(
        scan_id=scan.id,
        status=scan.status.value if hasattr(scan.status, "value") else str(scan.status),
        detection_type=scan.detection_type.value
        if scan.detection_type and hasattr(scan.detection_type, "value")
        else None,
        ocr_provider=scan.ocr_provider.value
        if scan.ocr_provider and hasattr(scan.ocr_provider, "value")
        else None,
        ocr_confidence=scan.ocr_confidence,
        fallback_used=scan.fallback_used,
        fallback_reason=scan.fallback_reason,
        diagnostic=diagnostic_payload,
        session_id=session_id,
        created_at=scan.created_at,
        processed_at=scan.processed_at,
    )
