"""Modèles Session + SessionAnswer + ExerciseTemplate."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Enum

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.scans import Diagnostic


class ExerciseType(str, enum.Enum):
    MCQ = "mcq"
    FILL_BLANK = "fill_blank"
    SHORT_TEXT = "short_text"
    DRAG_DROP = "drag_drop"


class SessionStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ExerciseTemplate(Base):
    """Template d'exercice généré par l'IA et stocké pour réutilisation."""

    __tablename__ = "exercise_templates"

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
    concept_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("concepts.id"),
        nullable=False,
        index=True,
    )
    type: Mapped[ExerciseType] = mapped_column(Enum(ExerciseType), nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    # Structure : { "prompt": "...", "options": [...], "answer": "B", "tts_text": "...", "explanation": "..." }
    template_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    locale: Mapped[str] = mapped_column(String(10), nullable=False, default="fr-KM")
    validated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    generated_by: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<ExerciseTemplate {self.id} {self.type} difficulty={self.difficulty}>"


class Session(Base):
    """Session de rattrapage (pack de 3-4 micro-exercices)."""

    __tablename__ = "sessions"

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
    diagnostic_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("diagnostics.id"),
        nullable=True,
    )
    target_concept_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("concepts.id"),
        nullable=False,
        index=True,
    )
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus),
        default=SessionStatus.IN_PROGRESS,
        nullable=False,
    )
    # Ordre des exercises_template_ids à présenter
    exercise_order: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    success_rate: Mapped[float | None] = mapped_column(Float, nullable=True)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    diagnostic: Mapped[Diagnostic | None] = relationship(back_populates="sessions")
    answers: Mapped[list[SessionAnswer]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Session {self.id} status={self.status} concept={self.target_concept_id}>"


class SessionAnswer(Base):
    """Réponse de l'élève à un exercice — déclenche update BKT."""

    __tablename__ = "session_answers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id"),
        nullable=False,
        index=True,
    )
    exercise_template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exercise_templates.id"),
        nullable=False,
    )
    student_answer: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Snapshot mastery avant et après update BKT
    mastery_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    mastery_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    session: Mapped[Session] = relationship(back_populates="answers")
