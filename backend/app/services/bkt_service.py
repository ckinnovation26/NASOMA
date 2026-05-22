"""Service BKT — Bayesian Knowledge Tracing.

Paramètres standards (cf. docs/architecture.md + strategie_Nasoma.md) :
  p_init    = 0.1   (probabilité maîtrise initiale)
  p_transit = 0.2   (probabilité d'apprendre par tentative)
  p_slip    = 0.1   (erreur d'inattention sur concept maîtrisé)
  p_guess   = 0.25  (réussite par chance sur concept non maîtrisé)

Règles métier (§18 BP) :
  R03 — Concept "maîtrisé" si 3 réussites consécutives sur 3 sessions différentes
  R04 — Concept "bloqué" si 2 échecs en 7 jours

Seuils :
  >= 0.85 : maîtrisé (vert)
  >= 0.50 : en cours (orange)
  <  0.50 : non maîtrisé (rouge)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mastery import StudentConceptMastery

logger = structlog.get_logger(__name__)

# Paramètres BKT (cf. §25 BP)
P_INIT = 0.1
P_TRANSIT = 0.2
P_SLIP = 0.1
P_GUESS = 0.25

# Seuils de statut
THRESHOLD_MASTERED = 0.85
THRESHOLD_IN_PROGRESS = 0.50


@dataclass(frozen=True)
class BktUpdateResult:
    """Résultat d'une mise à jour BKT."""

    mastery_before: float
    mastery_after: float
    status_before: str
    status_after: str
    became_mastered: bool
    became_blocked: bool


def bkt_update_formula(
    p_known: float,
    correct: bool,
    p_transit: float = P_TRANSIT,
    p_slip: float = P_SLIP,
    p_guess: float = P_GUESS,
) -> float:
    """Met à jour P(L) après observation — formule pure (cf. §25 BP).

    Args:
        p_known : probabilité actuelle que l'élève maîtrise le concept
        correct : True si bonne réponse, False sinon
        p_transit/p_slip/p_guess : paramètres BKT

    Returns:
        Nouvelle probabilité, clampée dans [0, 1].
    """
    if correct:
        numerator = p_known * (1 - p_slip)
        denominator = numerator + (1 - p_known) * p_guess
    else:
        numerator = p_known * p_slip
        denominator = numerator + (1 - p_known) * (1 - p_guess)

    if denominator <= 0:
        return p_known

    p_known_given_obs = numerator / denominator
    # Apprentissage : transition vers maîtrise
    p_known_next = p_known_given_obs + (1 - p_known_given_obs) * p_transit
    return min(max(p_known_next, 0.0), 1.0)


def status_for(p_known: float) -> str:
    """Statut visuel selon les seuils."""
    if p_known >= THRESHOLD_MASTERED:
        return "maitrise"
    if p_known >= THRESHOLD_IN_PROGRESS:
        return "en_cours"
    return "non_maitrise"


class BktService:
    """Persiste et met à jour les profils BKT par (student, concept)."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_or_create(
        self,
        student_id: uuid.UUID,
        concept_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> StudentConceptMastery:
        """Récupère le profil ou crée un nouveau avec p_init."""
        result = await self.db.execute(
            select(StudentConceptMastery).where(
                StudentConceptMastery.student_id == student_id,
                StudentConceptMastery.concept_id == concept_id,
            )
        )
        mastery = result.scalar_one_or_none()
        if mastery is None:
            mastery = StudentConceptMastery(
                student_id=student_id,
                concept_id=concept_id,
                tenant_id=tenant_id,
                mastery_probability=P_INIT,
            )
            self.db.add(mastery)
            await self.db.flush()
        return mastery

    async def record_answer(
        self,
        student_id: uuid.UUID,
        concept_id: uuid.UUID,
        tenant_id: uuid.UUID,
        correct: bool,
    ) -> BktUpdateResult:
        """Enregistre une réponse et met à jour le profil BKT."""
        mastery = await self.get_or_create(student_id, concept_id, tenant_id)

        before = mastery.mastery_probability
        status_before = status_for(before)
        after = bkt_update_formula(before, correct)

        mastery.mastery_probability = after
        mastery.attempts += 1
        mastery.last_practiced_at = datetime.now(UTC)
        if correct:
            mastery.successes += 1
            mastery.consecutive_successes += 1
        else:
            mastery.consecutive_successes = 0
            # R04 — Compteur d'échecs sur 7 jours glissants (simplifié)
            mastery.failures_last_7_days += 1

        await self.db.flush()

        status_after = status_for(after)
        became_mastered = (
            status_before != "maitrise"
            and status_after == "maitrise"
            and mastery.consecutive_successes >= 3      # R03 anti-luck
        )
        became_blocked = (
            status_before != "non_maitrise"
            and status_after == "non_maitrise"
            and mastery.failures_last_7_days >= 2       # R04
        )

        logger.info(
            "bkt.updated",
            student=str(student_id),
            concept=str(concept_id),
            correct=correct,
            p_before=round(before, 3),
            p_after=round(after, 3),
            became_mastered=became_mastered,
            became_blocked=became_blocked,
        )

        return BktUpdateResult(
            mastery_before=before,
            mastery_after=after,
            status_before=status_before,
            status_after=status_after,
            became_mastered=became_mastered,
            became_blocked=became_blocked,
        )

    async def get_weakest_concept_id(
        self,
        student_id: uuid.UUID,
        grade_level: str | None = None,
        subject_code: str | None = None,
    ) -> uuid.UUID | None:
        """Retourne l'ID du concept le plus faible — pour fallback exos.

        Utilise le critère "min mastery_probability". Si profil vide, retourne None
        (le caller doit alors choisir un concept fondamental du grade_level).
        """
        from app.models.concepts import Concept
        from app.models.subjects import Subject

        stmt = select(StudentConceptMastery).join(
            Concept, Concept.id == StudentConceptMastery.concept_id
        )
        if grade_level:
            stmt = stmt.where(Concept.grade_level == grade_level)
        if subject_code:
            stmt = stmt.join(Subject, Subject.id == Concept.subject_id).where(
                Subject.code == subject_code
            )
        stmt = stmt.where(StudentConceptMastery.student_id == student_id)
        stmt = stmt.order_by(StudentConceptMastery.mastery_probability.asc()).limit(1)

        result = await self.db.execute(stmt)
        mastery = result.scalar_one_or_none()
        return mastery.concept_id if mastery else None

    @staticmethod
    def cleanup_failures_window(mastery: StudentConceptMastery) -> None:
        """À appeler quotidiennement : reset le compteur 7 jours si last_practiced > 7j."""
        if mastery.last_practiced_at is None:
            return
        last = mastery.last_practiced_at
        if last.tzinfo is None:
            last = last.replace(tzinfo=UTC)
        if (datetime.now(UTC) - last) > timedelta(days=7):
            mastery.failures_last_7_days = 0
