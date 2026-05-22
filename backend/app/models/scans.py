"""Modèles Scan + Diagnostic + ScanArchive.

- `Scan` : workflow opérationnel (TTL 30j sur l'image originale)
- `Diagnostic` : résultat IA structuré
- `ScanArchive` : actif Moat #1 (corpus persistant indéfini)
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Enum

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.sessions import Session
    from app.models.subjects import Subject


class ScanStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    DONE_WITH_FALLBACK = "done_with_fallback"  # OCR difficile mais exos générés depuis profil (Always Give Value)
    FAILED = "failed"


class OcrProvider(str, enum.Enum):
    MLKIT_LOCAL = "mlkit_local"        # étage 1 (gratuit, on-device)
    CLOUD_VISION = "cloud_vision"      # étage 2 (~0,0015 $/page)
    GEMINI_FLASH = "gemini_flash"      # étage 3 (vision multimodale)
    GEMINI_FLASH_8B = "gemini_flash_8b"


class DetectionType(str, enum.Enum):
    """Résultat de la détection IA — l'app décide du flow UX à partir de ça.

    Backend = détection IA pure (qu'est-ce qui ne va pas).
    App     = décision UX (que proposer à l'utilisateur).
    """

    SUCCESS = "success"
    IMAGE_QUALITY_LOW = "image_quality_low"
    OCR_NO_TEXT = "ocr_no_text"
    NO_SCHOOL_WORK = "no_school_work"
    HANDWRITING_ILLEGIBLE = "handwriting_illegible"
    WRONG_PAGE = "wrong_page"
    CONCEPT_MAPPING_FAILED = "concept_mapping_failed"
    OCR_ERROR = "ocr_error"
    NETWORK_ERROR = "network_error"


class Scan(Base):
    """Workflow opérationnel d'un scan (TTL court image originale)."""

    __tablename__ = "scans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subjects.id"),
        nullable=True,
    )

    image_storage_key: Mapped[str] = mapped_column(String(256), nullable=False)
    thumbnail_storage_key: Mapped[str | None] = mapped_column(String(256), nullable=True)
    image_phash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    image_size_bytes: Mapped[int | None] = mapped_column(nullable=True)

    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus),
        default=ScanStatus.PENDING,
        nullable=False,
        index=True,
    )
    ocr_raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_provider: Mapped[OcrProvider | None] = mapped_column(Enum(OcrProvider), nullable=True)
    ocr_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Tracking coût IA (Moat budget control)
    ai_cost_usd: Mapped[float | None] = mapped_column(Float, default=0.0)
    ai_tokens_input: Mapped[int | None] = mapped_column(default=0)
    ai_tokens_output: Mapped[int | None] = mapped_column(default=0)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    grade_level: Mapped[str | None] = mapped_column(String(8), nullable=True)
    cached_from_phash: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fallback_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fallback_reason: Mapped[str | None] = mapped_column(String(120), nullable=True)
    detection_type: Mapped[DetectionType | None] = mapped_column(
        Enum(DetectionType),
        nullable=True,
    )
    detection_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    retry_of_scan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scans.id"),
        nullable=True,
    )
    retry_count: Mapped[int] = mapped_column(default=0, nullable=False)
    parent_chose_continue_without_rescan: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    subject: Mapped[Subject | None] = relationship()
    diagnostic: Mapped[Diagnostic | None] = relationship(
        back_populates="scan",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Scan {self.id} status={self.status} provider={self.ocr_provider}>"


class Diagnostic(Base):
    """Résultat de l'analyse IA d'un scan."""

    __tablename__ = "diagnostics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )
    scan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scans.id"),
        unique=True,
        nullable=False,
    )

    # Structure : [{ "exercise_index": 4, "concept_code": "MATH_CM2_RETENUE",
    #                "error_type": "missing_carry", "confidence": 0.87, ... }]
    detected_errors: Mapped[list] = mapped_column(JSON, nullable=False)
    concepts_affected: Mapped[list[uuid.UUID] | None] = mapped_column(
        ARRAY(UUID(as_uuid=True)),
        nullable=True,
    )
    summary_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_exercises_detected: Mapped[int] = mapped_column(default=0)
    correct_count: Mapped[int] = mapped_column(default=0)
    incorrect_count: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    scan: Mapped[Scan] = relationship(back_populates="diagnostic")
    sessions: Mapped[list[Session]] = relationship(back_populates="diagnostic")

    def __repr__(self) -> str:
        return f"<Diagnostic {self.id} {self.correct_count}/{self.total_exercises_detected}>"


class ScanArchive(Base):
    """Corpus persistant des scans (Moat #1).

    Différent de `scans` : ici on garde indéfiniment.
    """

    __tablename__ = "scan_archives"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    scan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scans.id"),
        nullable=False,
    )

    image_storage_key: Mapped[str] = mapped_column(String(256), nullable=False)
    thumbnail_storage_key: Mapped[str | None] = mapped_column(String(256), nullable=True)
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnostic_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    exercises_detected: Mapped[list | None] = mapped_column(JSON, nullable=True)
    concepts_touched: Mapped[list[uuid.UUID] | None] = mapped_column(
        ARRAY(UUID(as_uuid=True)),
        nullable=True,
    )
    scan_quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    subject: Mapped[str | None] = mapped_column(String(20), nullable=True)
    grade_level: Mapped[str | None] = mapped_column(String(8), nullable=True)
    is_archived_consent: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<ScanArchive {self.id} student={self.student_id}>"
