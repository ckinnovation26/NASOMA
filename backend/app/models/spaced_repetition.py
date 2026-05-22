"""Spaced Repetition (Moat #6) — révision espacée des concepts maîtrisés.

Cf. docs/strategie_Nasoma.md : "Un concept marqué maîtrisé n'est pas oublié.
Il est re-testé à J+1, J+7, J+30, J+90."

C'est la rotation forcée pédagogique qui distingue Nasoma d'un correcteur ponctuel.
Sans ça, l'élève "savait" en CM1 et "ne sait plus" en CM2.
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, SmallInteger, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime, Enum


from app.db.session import Base


class ReviewStatus(str, enum.Enum):
    SCHEDULED = "scheduled"      # à venir
    COMPLETED = "completed"      # passée avec succès → maîtrise confirmée
    FAILED = "failed"            # échec → concept retombe en cours
    SKIPPED = "skipped"          # ignorée (manqué la fenêtre)


class ReviewOutcome(str, enum.Enum):
    RETAINED = "retained"        # connaissance retenue (succès)
    FORGOTTEN = "forgotten"      # oublié → mini-rattrapage programmé
    PARTIAL = "partial"          # partiel → retest dans 2 jours


# Intervalles standards SR (en jours)
SR_INTERVALS_DAYS = [1, 7, 30, 90]


class SpacedReview(Base):
    """Une révision programmée d'un concept maîtrisé."""

    __tablename__ = "spaced_reviews"

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
    concept_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("concepts.id"),
        nullable=False,
        index=True,
    )
    scheduled_for: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    interval_days: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 1, 7, 30, 90
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus),
        default=ReviewStatus.SCHEDULED,
        nullable=False,
        index=True,
    )
    outcome: Mapped[ReviewOutcome | None] = mapped_column(
        Enum(ReviewOutcome),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    # Si échec : mastery_after pour tracking BKT
    mastery_before: Mapped[float | None] = mapped_column(nullable=True)
    mastery_after: Mapped[float | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<SpacedReview {self.id} concept={self.concept_id} "
            f"+{self.interval_days}j status={self.status}>"
        )
