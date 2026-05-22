"""Modèles Concept et ConceptPrerequisite — Knowledge Graph APC_KM (DAG)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.subjects import Subject


class Concept(Base):
    """Un concept pédagogique du curriculum."""

    __tablename__ = "concepts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subjects.id"),
        nullable=False,
        index=True,
    )

    # Code naming convention : SUBJECT_GRADE_TOPIC (ex: MATH_CM2_ADD_RETENUE)
    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_shikomori: Mapped[str | None] = mapped_column(String(200), nullable=True)
    grade_level: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    difficulty: Mapped[int] = mapped_column(SmallInteger, nullable=False)         # 1..5
    estimated_minutes: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    curriculum_refs: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    common_errors: Mapped[list | None] = mapped_column(JSON, nullable=True)
    example_exercise: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    subject: Mapped[Subject] = relationship(back_populates="concepts")

    # Self-referencing many-to-many via concept_prerequisites
    prerequisites: Mapped[list[Concept]] = relationship(
        secondary="concept_prerequisites",
        primaryjoin="Concept.id==ConceptPrerequisite.concept_id",
        secondaryjoin="Concept.id==ConceptPrerequisite.prereq_id",
        backref="dependents",
        viewonly=True,
    )

    def __repr__(self) -> str:
        return f"<Concept {self.code} difficulty={self.difficulty}>"


class ConceptPrerequisite(Base):
    """Arête du DAG : concept_id requires prereq_id."""

    __tablename__ = "concept_prerequisites"

    concept_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("concepts.id"),
        primary_key=True,
    )
    prereq_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("concepts.id"),
        primary_key=True,
    )
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
