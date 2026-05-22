"""Modèle StudentConceptMastery — profil BKT d'un élève par concept.

Paramètres BKT (cf. docs/architecture.md) :
  p_init = 0.1, p_transit = 0.2, p_slip = 0.1, p_guess = 0.25

Seuils :
  >= 0.85 : maîtrisé (vert)
  >= 0.50 : en cours (orange)
  <  0.50 : non maîtrisé (rouge)
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Float, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime

from app.db.session import Base


class StudentConceptMastery(Base):
    """État de maîtrise BKT d'un élève sur un concept."""

    __tablename__ = "student_concept_mastery"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=True,
    )
    concept_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("concepts.id"),
        primary_key=True,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )

    mastery_probability: Mapped[float] = mapped_column(Float, default=0.1, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    successes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    consecutive_successes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failures_last_7_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_practiced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    @property
    def status(self) -> str:
        """Statut visuel selon seuils BKT (R03/R04)."""
        if self.mastery_probability >= 0.85:
            return "maitrise"
        if self.mastery_probability >= 0.50:
            return "en_cours"
        return "non_maitrise"

    def __repr__(self) -> str:
        return (
            f"<Mastery student={self.student_id} concept={self.concept_id} "
            f"p={self.mastery_probability:.2f} status={self.status}>"
        )
