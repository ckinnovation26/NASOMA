"""Service Spaced Repetition (Moat #6).

Workflow :
1. Quand un concept atteint mastery >= 0.85 dans BKT → on programme 4 reviews :
   J+1, J+7, J+30, J+90
2. Cron quotidien matin : génère les sessions de révision du jour
3. L'élève passe la review → si réussi : RETAINED ; si échec : FORGOTTEN (BKT descend)
4. Si FORGOTTEN à J+1 ou J+7, on reprogramme à intervalle réduit (J+2)
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta

import structlog
from sqlalchemy import and_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.concepts import Concept
from app.models.mastery import StudentConceptMastery
from app.models.spaced_repetition import (
    SR_INTERVALS_DAYS,
    ReviewOutcome,
    ReviewStatus,
    SpacedReview,
)
from app.services.bkt_service import THRESHOLD_MASTERED, BktService

logger = structlog.get_logger(__name__)


class SpacedRepetitionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def schedule_reviews_for_concept(
        self,
        student_id: uuid.UUID,
        concept_id: uuid.UUID,
        tenant_id: uuid.UUID,
        from_date: date | None = None,
    ) -> list[SpacedReview]:
        """Crée les 4 reviews J+1/J+7/J+30/J+90 pour un concept fraîchement maîtrisé.

        Idempotent : si une review existe déjà à cette date et status=scheduled, on skip.
        """
        if from_date is None:
            from_date = datetime.now(UTC).date()

        reviews: list[SpacedReview] = []
        for interval in SR_INTERVALS_DAYS:
            scheduled = from_date + timedelta(days=interval)
            # Check existing scheduled review for same (student, concept, scheduled_for)
            existing_stmt = select(SpacedReview).where(
                SpacedReview.student_id == student_id,
                SpacedReview.concept_id == concept_id,
                SpacedReview.scheduled_for == scheduled,
                SpacedReview.status == ReviewStatus.SCHEDULED,
            )
            existing = (await self.db.execute(existing_stmt)).scalar_one_or_none()
            if existing:
                continue
            review = SpacedReview(
                tenant_id=tenant_id,
                student_id=student_id,
                concept_id=concept_id,
                scheduled_for=scheduled,
                interval_days=interval,
                status=ReviewStatus.SCHEDULED,
            )
            self.db.add(review)
            reviews.append(review)

        await self.db.flush()
        logger.info(
            "sr.scheduled",
            student=str(student_id),
            concept=str(concept_id),
            count=len(reviews),
        )
        return reviews

    async def get_due_today(
        self, student_id: uuid.UUID, target_date: date | None = None
    ) -> list[tuple[SpacedReview, Concept]]:
        """Retourne les reviews dues aujourd'hui pour un élève."""
        if target_date is None:
            target_date = datetime.now(UTC).date()

        stmt = (
            select(SpacedReview, Concept)
            .join(Concept, Concept.id == SpacedReview.concept_id)
            .where(
                SpacedReview.student_id == student_id,
                SpacedReview.scheduled_for <= target_date,
                SpacedReview.status == ReviewStatus.SCHEDULED,
            )
            .order_by(SpacedReview.scheduled_for.asc(), SpacedReview.interval_days.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.all())

    async def complete_review(
        self,
        review_id: uuid.UUID,
        student_id: uuid.UUID,
        correct: bool,
    ) -> dict:
        """L'élève répond à une review.

        - correct=True → RETAINED, mastery boost
        - correct=False → FORGOTTEN, mastery drop + replanifier mini-review J+2
        """
        review = await self.db.get(SpacedReview, review_id)
        if review is None or review.student_id != student_id:
            raise ValueError("Review introuvable.")
        if review.status != ReviewStatus.SCHEDULED:
            raise ValueError("Review déjà traitée.")

        # Update BKT
        bkt = BktService(self.db)
        update_result = await bkt.record_answer(
            student_id=student_id,
            concept_id=review.concept_id,
            tenant_id=review.tenant_id,
            correct=correct,
        )

        review.mastery_before = update_result.mastery_before
        review.mastery_after = update_result.mastery_after
        review.completed_at = datetime.now(UTC)

        if correct:
            review.status = ReviewStatus.COMPLETED
            review.outcome = ReviewOutcome.RETAINED
            logger.info("sr.review_retained", review_id=str(review_id))
        else:
            review.status = ReviewStatus.FAILED
            review.outcome = ReviewOutcome.FORGOTTEN
            logger.info("sr.review_forgotten", review_id=str(review_id))

            # Reprogrammer une mini-review à J+2 si l'oubli est précoce
            if review.interval_days <= 7:
                mini = SpacedReview(
                    tenant_id=review.tenant_id,
                    student_id=student_id,
                    concept_id=review.concept_id,
                    scheduled_for=datetime.now(UTC).date() + timedelta(days=2),
                    interval_days=2,
                    status=ReviewStatus.SCHEDULED,
                )
                self.db.add(mini)

        await self.db.flush()
        return {
            "review_id": str(review_id),
            "status": review.status.value,
            "outcome": review.outcome.value if review.outcome else None,
            "mastery_before": review.mastery_before,
            "mastery_after": review.mastery_after,
            "interval_days": review.interval_days,
        }

    async def auto_schedule_for_newly_mastered(self) -> int:
        """Cron quotidien — détecte les concepts récemment passés à maîtrisé sans review programmée.

        Pour chaque (student, concept) avec mastery >= 0.85 et pas de SR scheduled :
        → programme les 4 intervals.
        """
        stmt = (
            select(StudentConceptMastery)
            .where(
                StudentConceptMastery.mastery_probability >= THRESHOLD_MASTERED,
            )
        )
        result = await self.db.execute(stmt)
        masteries = list(result.scalars().all())

        count = 0
        for m in masteries:
            # Vérifier qu'aucune SR scheduled n'existe déjà pour ce couple
            existing_stmt = select(SpacedReview).where(
                SpacedReview.student_id == m.student_id,
                SpacedReview.concept_id == m.concept_id,
                SpacedReview.status == ReviewStatus.SCHEDULED,
            ).limit(1)
            existing = (await self.db.execute(existing_stmt)).scalar_one_or_none()
            if existing:
                continue
            await self.schedule_reviews_for_concept(
                student_id=m.student_id,
                concept_id=m.concept_id,
                tenant_id=m.tenant_id,
            )
            count += 1

        await self.db.commit()
        logger.info("sr.auto_scheduled_batch", concepts_count=count)
        return count
