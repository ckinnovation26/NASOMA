"""OCR Worker — handler Cloud Tasks pour le pipeline de traitement scan asynchrone.

Appelé par Cloud Tasks (queue "ocr-worker-queue") via HTTP POST authentifié OIDC.
Le résultat est publié dans Firestore pour polling par l'app Flutter.

Codes de retour :
- 200 : traitement terminé (succès ou fallback) — Cloud Tasks ne réessaie pas
- 400 : payload invalide / scan introuvable — Cloud Tasks NE réessaie pas (dead-letter)
- 503 : erreur transitoire (DB, Gemini timeout) — Cloud Tasks réessaie selon backoff
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, status
from google.api_core.exceptions import GoogleAPICallError
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.firestore import get_firestore_client
from app.db.session import get_db
from app.models.scans import Scan, ScanStatus
from app.services.scan_processor_service import ScanProcessorService

logger = structlog.get_logger(__name__)

router = APIRouter()

_FIRESTORE_SCANS_COLLECTION = "scans"


class OcrTaskPayload(BaseModel):
    """Payload JSON envoyé par Cloud Tasks."""

    scan_id: uuid.UUID
    student_id: uuid.UUID
    tenant_id: uuid.UUID
    image_storage_key: str
    subject_code: str = "MATH"
    grade_level: str | None = None
    mlkit_text: str | None = None
    mlkit_confidence: float | None = Field(default=None, ge=0.0, le=1.0)


@router.post(
    "/workers/ocr",
    status_code=status.HTTP_200_OK,
    summary="Handler Cloud Tasks — traitement OCR asynchrone d'un scan",
    include_in_schema=False,
)
async def handle_ocr_task(
    payload: OcrTaskPayload,
    db: AsyncSession = Depends(get_db),
    x_cloudtasks_taskname: str | None = Header(default=None),
    x_cloudtasks_taskretrycount: str | None = Header(default=None),
) -> dict:
    """Traite un scan via le pipeline OCR complet et publie le résultat dans Firestore.

    Le header X-CloudTasks-TaskRetryCount permet d'ajuster le comportement
    en cas de réessai (ex. sauter ML Kit si déjà échoué).
    """
    retry_count = int(x_cloudtasks_taskretrycount or 0)
    log = logger.bind(
        scan_id=str(payload.scan_id),
        student_id=str(payload.student_id),
        task_name=x_cloudtasks_taskname,
        retry_count=retry_count,
    )
    log.info("ocr_worker.received")

    # ── Vérifier que le scan existe et n'est pas déjà traité ──
    result = await db.execute(select(Scan).where(Scan.id == payload.scan_id))
    scan = result.scalar_one_or_none()

    if scan is None:
        log.warning("ocr_worker.scan_not_found")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scan {payload.scan_id} introuvable. Tâche annulée.",
        )

    if scan.status in (ScanStatus.DONE, ScanStatus.DONE_WITH_FALLBACK):
        log.info("ocr_worker.already_processed", scan_status=scan.status)
        return {"status": "already_processed", "scan_id": str(payload.scan_id)}

    # ── Charger l'image depuis Cloud Storage ──
    image_bytes = await _fetch_image_bytes(payload.image_storage_key, log)
    if image_bytes is None:
        if retry_count < 3:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Image temporairement inaccessible en Cloud Storage.",
            )
        # Après 3 tentatives, on marque en failed et on ne réessaie plus
        await _mark_scan_failed(scan, db, "Image inaccessible après 3 tentatives.")
        await _publish_firestore(
            payload.scan_id,
            status="failed",
            detection_type="storage_error",
            diagnostic_id=None,
            session_id=None,
            ocr_confidence=None,
            quota_remaining_after=None,
            summary_text="Impossible de lire l'image. Réessayez.",
            log=log,
        )
        return {"status": "failed", "reason": "storage_unavailable"}

    # ── Lancer le pipeline ──
    processor = ScanProcessorService(db)
    try:
        processing_result = await processor.process(
            student_id=payload.student_id,
            tenant_id=payload.tenant_id,
            image_bytes=image_bytes,
            image_storage_key=payload.image_storage_key,
            subject_code=payload.subject_code,
            grade_level=payload.grade_level,
            mlkit_text=payload.mlkit_text,
            mlkit_confidence=payload.mlkit_confidence,
        )
    except GoogleAPICallError as exc:
        # Erreur transitoire GCP (Vision API, Gemini) → 503 pour retry
        log.warning("ocr_worker.gcp_transient_error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur GCP transitoire : {exc!s}",
        ) from exc
    except ValueError as exc:
        # Donnée invalide (user inconnu, etc.) → 400 pour dead-letter
        log.error("ocr_worker.invalid_data", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        # Erreur interne inattendue → 503 pour retry (jusqu'à max_attempts)
        log.error("ocr_worker.unexpected_error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Erreur interne inattendue.",
        ) from exc

    await db.commit()

    # ── Publier le résultat dans Firestore (polling mobile) ──
    await _publish_firestore(
        scan_id=payload.scan_id,
        status=processing_result.status.value,
        detection_type=processing_result.detection_type.value,
        diagnostic_id=processing_result.diagnostic_id,
        session_id=processing_result.session_id,
        ocr_confidence=processing_result.ocr_confidence,
        quota_remaining_after=processing_result.quota_remaining_after,
        summary_text=processing_result.summary_text,
        log=log,
    )

    log.info(
        "ocr_worker.completed",
        status=processing_result.status.value,
        detection_type=processing_result.detection_type.value,
        cached=processing_result.cached_from_phash,
        quota_remaining=processing_result.quota_remaining_after,
    )
    return {
        "status": processing_result.status.value,
        "scan_id": str(payload.scan_id),
        "detection_type": processing_result.detection_type.value,
        "diagnostic_id": str(processing_result.diagnostic_id)
        if processing_result.diagnostic_id
        else None,
    }


# ──────────────────────────────────────────────
#  Helpers internes
# ──────────────────────────────────────────────

async def _fetch_image_bytes(storage_key: str, log: structlog.BoundLogger) -> bytes | None:
    """Télécharge l'image depuis Cloud Storage. Retourne None si indisponible."""
    try:
        from google.cloud import storage as gcs

        from app.core.config import settings

        gcs_client = gcs.Client(project=settings.gcp_project_id)
        bucket = gcs_client.bucket(settings.gcp_storage_bucket)
        blob = bucket.blob(storage_key)
        return blob.download_as_bytes(timeout=30)
    except Exception as exc:
        log.warning("ocr_worker.gcs_fetch_failed", storage_key=storage_key, error=str(exc))
        return None


async def _mark_scan_failed(scan: Scan, db: AsyncSession, reason: str) -> None:
    scan.status = ScanStatus.FAILED
    scan.error_message = reason
    scan.processed_at = datetime.now(UTC)
    await db.commit()


async def _publish_firestore(
    scan_id: uuid.UUID,
    status: str,
    detection_type: str,
    diagnostic_id: uuid.UUID | None,
    session_id: uuid.UUID | None,
    ocr_confidence: float | None,
    quota_remaining_after: int | None,
    summary_text: str,
    log: structlog.BoundLogger,
) -> None:
    """Publie le résultat dans Firestore pour polling par l'app Flutter.

    Collection : scans/{scan_id}
    L'app Flutter poll /scans/{scan_id}/result jusqu'à ce que status != "processing".
    """
    try:
        fs = get_firestore_client()
        doc_ref = fs.collection(_FIRESTORE_SCANS_COLLECTION).document(str(scan_id))
        await doc_ref.set(
            {
                "scan_id": str(scan_id),
                "status": status,
                "detection_type": detection_type,
                "diagnostic_id": str(diagnostic_id) if diagnostic_id else None,
                "session_id": str(session_id) if session_id else None,
                "ocr_confidence": ocr_confidence,
                "quota_remaining_after": quota_remaining_after,
                "summary_text": summary_text,
                "processed_at": datetime.now(UTC).isoformat(),
            },
            merge=False,
        )
    except Exception as exc:
        # Firestore non critique : l'app peut aussi poll le backend REST
        log.warning("ocr_worker.firestore_publish_failed", error=str(exc))
