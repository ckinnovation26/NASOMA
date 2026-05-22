"""Service ExerciseGenerator — génère des micro-exercices via Gemini Flash-8B.

Utilise responseSchema strict + temperature 0.2 (cf. §24 BP Prompt 3).
Garde-fous :
  - Whitelist concept_code obligatoire
  - Pas de noms étrangers (préférer Ali, Fatima, Said, Mariama)
  - Pas de prix en € (KMF ou contexte abstrait)
  - Phrases < 15 mots, vocabulaire adapté grade_level
  - Vertex AI Safety BLOCK_MEDIUM_AND_ABOVE
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.concepts import Concept
from app.models.sessions import ExerciseTemplate, ExerciseType

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class GeneratedExercise:
    """Exercice généré (avant persistance)."""

    type: ExerciseType
    prompt: str
    options: list[str] | None
    correct_answer: str
    explanation_short: str
    tts_text: str | None
    difficulty: int


class ExerciseGeneratorService:
    """Génère et persiste des exercices ciblés sur un concept."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def generate_for_concept(
        self,
        concept_id: uuid.UUID,
        tenant_id: uuid.UUID,
        count: int = 4,
        locale: str = "fr-KM",
    ) -> list[ExerciseTemplate]:
        """Génère N exercices pour un concept et les persiste."""
        concept = await self.db.get(Concept, concept_id)
        if concept is None:
            raise ValueError(f"Concept {concept_id} not found")

        try:
            generated = await self._call_gemini(
                concept_name=concept.name,
                concept_code=concept.code,
                grade_level=concept.grade_level,
                age=self._estimate_age(concept.grade_level),
                count=count,
            )
        except NotImplementedError:
            # Stub Sprint 2 — exemples placeholders pour le concept
            generated = self._stub_exercises(concept, count)

        templates: list[ExerciseTemplate] = []
        for i, ex in enumerate(generated):
            template = ExerciseTemplate(
                tenant_id=tenant_id,
                concept_id=concept_id,
                type=ex.type,
                difficulty=ex.difficulty,
                locale=locale,
                template_json={
                    "prompt": ex.prompt,
                    "options": ex.options,
                    "answer": ex.correct_answer,
                    "explanation_short": ex.explanation_short,
                    "tts_text": ex.tts_text,
                    "order": i,
                },
                generated_by=settings.gemini_model_generate,
            )
            self.db.add(template)
            templates.append(template)

        await self.db.flush()
        logger.info(
            "exercises.generated",
            concept=concept.code,
            count=len(templates),
        )
        return templates

    # ──────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────
    def _estimate_age(self, grade_level: str) -> int:
        """Estimation âge selon niveau (pour adapter vocabulaire)."""
        return {"CM1": 9, "CM2": 10, "6E": 11}.get(grade_level, 10)

    def _stub_exercises(self, concept: Concept, count: int) -> list[GeneratedExercise]:
        """Stub Sprint 2 — exemples pour un concept (dev only)."""
        examples = []
        for i in range(count):
            examples.append(
                GeneratedExercise(
                    type=ExerciseType.MCQ,
                    prompt=f"[STUB] Exercice {i + 1} sur {concept.name}",
                    options=["A", "B", "C", "D"],
                    correct_answer="B",
                    explanation_short=f"Réponse B parce que {concept.name}",
                    tts_text=concept.name,
                    difficulty=min(1 + i // 2, 4),
                )
            )
        return examples

    async def _call_gemini(
        self,
        concept_name: str,
        concept_code: str,
        grade_level: str,
        age: int,
        count: int,
    ) -> list[GeneratedExercise]:
        """Appel Gemini Flash-8B (Sprint 2.5)."""
        if settings.app_env == "dev" and not settings.gemini_api_key:
            raise NotImplementedError("Gemini exercises à implémenter Sprint 2.5")

        # Implémentation réelle (Sprint 2.5)
        # Use response_schema with array of exercise objects
        # temperature=0.2, top_p=0.8

        raise NotImplementedError("Gemini exercises à implémenter Sprint 2.5")

    # ──────────────────────────────────────────────
    #  Fallback "Always Give Value"
    # ──────────────────────────────────────────────
    async def generate_fallback_for_student(
        self,
        student_id: uuid.UUID,
        tenant_id: uuid.UUID,
        grade_level: str,
        subject_code: str = "MATH",
    ) -> list[ExerciseTemplate]:
        """Génère des exos depuis le profil BKT (concept le plus faible).

        Appelé quand l'OCR échoue (fallback policy — Always Give Value).
        Cf. docs/pricing.md "Politique Always Give Value".
        """
        from app.services.bkt_service import BktService

        bkt = BktService(self.db)
        concept_id = await bkt.get_weakest_concept_id(
            student_id=student_id,
            grade_level=grade_level,
            subject_code=subject_code,
        )

        if concept_id is None:
            # Profil vide → choisir un concept fondamental du grade_level
            stmt = (
                select(Concept.id)
                .join(Concept.subject)
                .where(Concept.grade_level == grade_level)
                .order_by(Concept.difficulty.asc())
                .limit(1)
            )
            result = await self.db.execute(stmt)
            concept_id = result.scalar_one_or_none()
            if concept_id is None:
                logger.warning(
                    "fallback.no_concept_available",
                    student=str(student_id),
                    grade=grade_level,
                )
                return []

        logger.info(
            "fallback.generating",
            student=str(student_id),
            concept=str(concept_id),
        )
        return await self.generate_for_concept(
            concept_id=concept_id,
            tenant_id=tenant_id,
            count=settings.fallback_default_exercises_count,
        )
