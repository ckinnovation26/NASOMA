"""Modèles FallbackContext + VendorAssistanceRequest (politique Always Give Value)."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime, Enum

from app.db.session import Base


class AssistanceReason(str, enum.Enum):
    """Raison déclenchée par le parent pour assistance."""

    CAMERA_DEFECTIVE = "camera_defective"
    PHOTO_TAKING_SKILL = "photo_taking_skill"
    HOMEWORK_REALLY_ILLEGIBLE = "homework_really_illegible"
    REPEAT_FAILURES = "repeat_failures"
    UNKNOWN = "unknown"


class AssistanceStatus(str, enum.Enum):
    PENDING = "pending"             # créé, vendeur pas encore notifié
    NOTIFIED = "notified"           # vendeur notifié
    CONTACTED = "contacted"         # vendeur a contacté le parent
    RESOLVED = "resolved"           # problème résolu
    DECLINED = "declined"           # parent refuse l'aide
    EXPIRED = "expired"             # > 14j sans action


class FallbackContext(Base):
    """Contexte fourni par le parent quand un scan échoue (étape 2 du flow).

    Saisi via une modal après un retry illisible.
    Utilisé par ExerciseGeneratorService pour mieux cibler les exos fallback.
    """

    __tablename__ = "fallback_contexts"

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
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    subject_code: Mapped[str] = mapped_column(String(20), nullable=False)
    grade_level: Mapped[str] = mapped_column(String(8), nullable=False)
    recent_grade: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    max_grade: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True, default=20.0
    )
    parent_comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    extracted_keywords: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<FallbackContext scan={self.scan_id} subject={self.subject_code}>"


class VendorAssistanceRequest(Base):
    """Demande d'assistance vendeur — 3+ scans illisibles en 7j.

    Le vendeur de proximité (dernier en historique) reçoit notification interne.
    Formation 1er niveau dispensée par Nasoma (cf. strategie_Nasoma.md).
    """

    __tablename__ = "vendor_assistance_requests"

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
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    vendor_id: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)

    reason: Mapped[AssistanceReason] = mapped_column(
        Enum(AssistanceReason),
        nullable=False,
    )
    failed_scans_count_7d: Mapped[int] = mapped_column(default=0)
    status: Mapped[AssistanceStatus] = mapped_column(
        Enum(AssistanceStatus),
        default=AssistanceStatus.PENDING,
        nullable=False,
        index=True,
    )
    courtesy_rescan_granted: Mapped[bool] = mapped_column(default=False, nullable=False)

    notes_internal: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    notified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    contacted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<VendorAssistanceRequest {self.id} reason={self.reason} "
            f"status={self.status}>"
        )
