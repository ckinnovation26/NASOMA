"""Modèles indicateurs CT/MT/LT — cœur de valeur Nasoma.

Cf. docs/strategie_Nasoma.md : "Nasoma construit un élève" — trajectoire
d'apprentissage longitudinale qui nous différencie de Google.

- `mastery_snapshots` : photo quotidienne du BKT par concept (séries temporelles)
- `student_indicators` : indicateurs CT/MT/LT pré-calculés + recommandations
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, Float, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime, Enum

from app.db.session import Base


class IndicatorHorizon(str, enum.Enum):
    """Horizons temporels des indicateurs (cf. docs/strategie_Nasoma.md)."""

    CT = "ct"          # Court terme : aujourd'hui (push + écran home)
    MT = "mt"          # Moyen terme : semaine + mois (SMS parent + dashboard)
    LT = "lt"          # Long terme : trimestre + année (rapport agrégé + examen blanc)


class MasterySnapshot(Base):
    """Snapshot quotidien du BKT par (student, concept).

    Cron job à 02:00 locale UTC : capture l'état actuel de chaque profil
    StudentConceptMastery → enregistre une ligne par jour par concept.

    Sert à :
    - Calculer les tendances (pente de régression CT/MT/LT)
    - Détecter régressions / stagnation / progression
    - Alimenter les graphiques de trajectoire
    """

    __tablename__ = "mastery_snapshots"

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
    snapshot_date: Mapped[date] = mapped_column(Date, primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )
    mastery_probability: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class StudentIndicators(Base):
    """Indicateurs CT/MT/LT agrégés + recommandations d'action.

    Calculés quotidiennement par cron pour chaque utilisateur actif.
    Le résultat est mis en cache ici pour servir les endpoints en < 100 ms.
    """

    __tablename__ = "student_indicators"

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
    horizon: Mapped[IndicatorHorizon] = mapped_column(
        Enum(IndicatorHorizon),
        nullable=False,
        index=True,
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)

    # Métriques agrégées (clés possibles selon horizon, cf. docs/api.md)
    # CT : { concepts_practiced_today, mastery_avg_today, delta_vs_yesterday, blocked_concept }
    # MT : { concepts_acquired, concepts_blocked, mastery_trend_slope, scan_frequency_per_week }
    # LT : { concepts_acquired_total, concepts_remaining_curriculum, projected_completion_date, risk_flags }
    metrics: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Recommandations d'action (push pour CT, conseils MT, décision pédagogique LT)
    recommendations: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<StudentIndicators {self.horizon} {self.period_start}→{self.period_end} "
            f"student={self.student_id}>"
        )
