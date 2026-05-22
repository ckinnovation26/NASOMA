"""ScanProcessor — orchestrateur du pipeline complet de traitement d'un scan.

Workflow (cf. docs/architecture.md "Flux de scan complet") :
  1. Vérifier quota (pré-flight)
  2. Compresser/valider image (taille, format)
  3. Calculer pHash → vérifier cache 24h
  4. OCR pipeline 3 étages
  5. Si OCR low confidence OU no exercises → FALLBACK exos depuis profil BKT
  6. Sinon : extraire exercices → mapper concepts → générer exos remédiation
  7. Créer Diagnostic + Session
  8. Archiver dans scan_archives (Moat #1)
  9. Décrémenter quota Firestore (atomique)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scans import (
    DetectionType,
    Diagnostic,
    OcrProvider,
    Scan,
    ScanArchive,
    ScanStatus,
)
from app.models.sessions import Session, SessionStatus
from app.models.subjects import Subject
from app.models.users import User
from app.services.bkt_service import BktService
from app.services.concept_mapper_service import ConceptMapperService
from app.services.exercise_generator_service import ExerciseGeneratorService
from app.services.ocr_service import MlkitResult, OcrService
from app.services.phash_service import PhashService, compute_phash
from app.services.quota_service import QuotaService

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class ScanProcessingResult:
    """Résultat final du traitement d'un scan.

    Backend = détection IA pure (detection_type + diagnostic si SUCCESS).
    App = décision UX (proposer retry, modal contexte, assistance) selon detection_type.
    """

    scan_id: uuid.UUID
    status: ScanStatus
    detection_type: DetectionType
    detection_details: dict | None
    diagnostic_id: uuid.UUID | None
    session_id: uuid.UUID | None
    cached_from_phash: bool
    ocr_confidence: float | None
    summary_text: str
    quota_remaining_after: int


class ScanProcessorService:
    """Orchestrateur principal — chaîne tous les services."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.ocr = OcrService()
        self.phash = PhashService(db)
        self.mapper = ConceptMapperService(db)
        self.exercises = ExerciseGeneratorService(db)
        self.bkt = BktService(db)
        self.quota = QuotaService()

    async def process(
        self,
        student_id: uuid.UUID,
        tenant_id: uuid.UUID,
        image_bytes: bytes,
        image_storage_key: str,
        subject_code: str = "MATH",
        grade_level: str | None = None,
        mlkit_text: str | None = None,
        mlkit_confidence: float | None = None,
    ) -> ScanProcessingResult:
        """Traite un scan end-to-end. Idempotent via pHash cache 24h."""
        user = await self.db.get(User, student_id)
        if user is None:
            raise ValueError(f"User {student_id} not found")

        effective_grade = grade_level or user.grade_level or "CM2"

        # ─── 1. pHash + cache check ───
        new_phash = compute_phash(image_bytes)
        cached = await self.phash.find_cached_scan(student_id, new_phash)
        if cached and cached.diagnostic:
            logger.info("scan.cache_hit_no_decrement", scan=str(cached.id))
            return ScanProcessingResult(
                scan_id=cached.id,
                status=cached.status,
                detection_type=DetectionType.SUCCESS,
                detection_details={"cached": True},
                diagnostic_id=cached.diagnostic.id,
                session_id=None,
                cached_from_phash=True,
                ocr_confidence=cached.ocr_confidence,
                summary_text=cached.diagnostic.summary_text or "Diagnostic en cache.",
                quota_remaining_after=-1,
            )

        # ─── 2. Créer le Scan (pending) ───
        subject_id = await self._resolve_subject_id(tenant_id, subject_code)
        scan = Scan(
            tenant_id=tenant_id,
            student_id=student_id,
            subject_id=subject_id,
            image_storage_key=image_storage_key,
            image_phash=new_phash,
            image_size_bytes=len(image_bytes),
            status=ScanStatus.PROCESSING,
            grade_level=effective_grade,
        )
        self.db.add(scan)
        await self.db.flush()

        # ─── 3. Décrémenter quota Firestore (atomic) ───
        try:
            quota_remaining = await self.quota.consume_scan(student_id)
        except Exception as e:
            logger.error("quota.consume_failed", error=str(e))
            scan.status = ScanStatus.FAILED
            scan.error_message = str(e)
            await self.db.flush()
            raise

        # ─── 4. OCR pipeline ───
        mlkit = (
            MlkitResult(text=mlkit_text, confidence=mlkit_confidence)
            if mlkit_text is not None and mlkit_confidence is not None
            else None
        )
        try:
            ocr_result = await self.ocr.run(image_bytes, mlkit_result=mlkit)
        except Exception as e:
            logger.error("ocr.pipeline_failed", error=str(e))
            return await self._detection_failure(
                scan,
                detection_type=DetectionType.OCR_ERROR,
                details={"error": str(e)[:200]},
                summary="Erreur technique lors de la lecture de l'image.",
                quota_remaining=quota_remaining,
            )

        scan.ocr_raw_text = ocr_result.text
        scan.ocr_provider = ocr_result.provider
        scan.ocr_confidence = ocr_result.confidence
        scan.ai_cost_usd = ocr_result.cost_usd

        # ─── 5. Détection : OCR vide ou faible confiance ───
        if not ocr_result.text.strip():
            return await self._detection_failure(
                scan,
                detection_type=DetectionType.OCR_NO_TEXT,
                details={"confidence": ocr_result.confidence},
                summary="Aucun texte détecté dans l'image.",
                quota_remaining=quota_remaining,
            )
        if ocr_result.needs_fallback:
            return await self._detection_failure(
                scan,
                detection_type=DetectionType.IMAGE_QUALITY_LOW,
                details={"confidence": ocr_result.confidence},
                summary="Qualité d'image insuffisante pour lire la copie.",
                quota_remaining=quota_remaining,
            )

        # ─── 6. Pipeline complet : extraction structurée → mapping → exos ───
        # NOTE Sprint 2 : extraction structurée est un appel Gemini Flash en vision
        # On simule ici avec une heuristique simple : on prend le texte OCR brut
        # comme une "erreur" et on mappe au concept le plus probable.
        # Vrai pipeline = appel Gemini avec responseSchema (Sprint 2.5).
        mapping = await self.mapper.map_error(
            error_description=ocr_result.text[:200],
            statement=ocr_result.text[:200],
            grade_level=effective_grade,
            subject_code=subject_code,
        )

        if mapping is None:
            return await self._detection_failure(
                scan,
                detection_type=DetectionType.CONCEPT_MAPPING_FAILED,
                details={"ocr_text_preview": ocr_result.text[:120]},
                summary="Texte lu mais aucun concept curriculum identifié.",
                quota_remaining=quota_remaining,
            )

        # ─── 7. Créer le diagnostic ───
        diagnostic = Diagnostic(
            tenant_id=tenant_id,
            scan_id=scan.id,
            detected_errors=[
                {
                    "exercise_index": 1,
                    "concept_code": mapping.concept_code,
                    "error_category": mapping.error_category,
                    "confidence": mapping.confidence,
                }
            ],
            concepts_affected=[mapping.concept_id],
            summary_text=f"Difficulté détectée sur : {mapping.concept_code}",
            total_exercises_detected=1,
            correct_count=0,
            incorrect_count=1,
        )
        self.db.add(diagnostic)
        await self.db.flush()

        # ─── 8. Générer les exos de remédiation ───
        templates = await self.exercises.generate_for_concept(
            concept_id=mapping.concept_id,
            tenant_id=tenant_id,
            count=4,
        )

        # ─── 9. Créer la session ───
        session = Session(
            tenant_id=tenant_id,
            student_id=student_id,
            diagnostic_id=diagnostic.id,
            target_concept_id=mapping.concept_id,
            status=SessionStatus.IN_PROGRESS,
            exercise_order=[str(t.id) for t in templates],
        )
        self.db.add(session)

        # ─── 10. Initialiser/MAJ BKT du concept détecté (échec implicite) ───
        await self.bkt.record_answer(
            student_id=student_id,
            concept_id=mapping.concept_id,
            tenant_id=tenant_id,
            correct=False,
        )

        # ─── 11. Archiver dans corpus (Moat #1) ───
        archive = ScanArchive(
            tenant_id=tenant_id,
            student_id=student_id,
            scan_id=scan.id,
            image_storage_key=image_storage_key,
            ocr_text=ocr_result.text,
            diagnostic_summary=diagnostic.summary_text,
            exercises_detected=diagnostic.detected_errors,
            concepts_touched=[mapping.concept_id],
            scan_quality_score=ocr_result.confidence,
            subject=subject_code,
            grade_level=effective_grade,
        )
        self.db.add(archive)

        # ─── 12. Finalisation ───
        scan.status = ScanStatus.DONE
        scan.detection_type = DetectionType.SUCCESS
        scan.processed_at = datetime.now(UTC)
        await self.db.flush()

        return ScanProcessingResult(
            scan_id=scan.id,
            status=scan.status,
            detection_type=DetectionType.SUCCESS,
            detection_details=None,
            diagnostic_id=diagnostic.id,
            session_id=session.id,
            cached_from_phash=False,
            ocr_confidence=ocr_result.confidence,
            summary_text=diagnostic.summary_text or "",
            quota_remaining_after=quota_remaining,
        )

    # ──────────────────────────────────────────────
    #  Échec de détection — retourne juste la detection_type
    #  L'app décide ensuite (retry, modal contexte, assistance, etc.)
    # ──────────────────────────────────────────────
    async def _detection_failure(
        self,
        scan: Scan,
        detection_type: DetectionType,
        details: dict | None,
        summary: str,
        quota_remaining: int,
    ) -> ScanProcessingResult:
        """L'IA n'a pas pu produire un diagnostic. L'app va décider quoi proposer."""
        logger.info(
            "scan.detection_failure",
            scan=str(scan.id),
            detection_type=detection_type.value,
            student=str(scan.student_id),
        )

        scan.status = ScanStatus.DONE_WITH_FALLBACK
        scan.detection_type = detection_type
        scan.detection_details = details
        scan.fallback_used = False  # pas encore, l'app va décider
        scan.fallback_reason = detection_type.value
        scan.processed_at = datetime.now(UTC)
        await self.db.flush()

        return ScanProcessingResult(
            scan_id=scan.id,
            status=scan.status,
            detection_type=detection_type,
            detection_details=details,
            diagnostic_id=None,
            session_id=None,
            cached_from_phash=False,
            ocr_confidence=scan.ocr_confidence,
            summary_text=summary,
            quota_remaining_after=quota_remaining,
        )

    async def _resolve_subject_id(
        self, tenant_id: uuid.UUID, subject_code: str
    ) -> uuid.UUID | None:
        stmt = select(Subject.id).where(
            Subject.tenant_id == tenant_id, Subject.code == subject_code
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
