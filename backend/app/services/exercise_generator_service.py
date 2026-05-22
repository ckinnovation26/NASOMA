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

import asyncio
import json
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
        """Génère des exercices via Gemini Flash-8B avec responseSchema JSON."""
        if not settings.gemini_api_key:
            raise NotImplementedError("GEMINI_API_KEY non configurée")

        import google.generativeai as genai  # noqa: PLC0415
        from google.generativeai.types import HarmBlockThreshold, HarmCategory  # noqa: PLC0415

        genai.configure(api_key=settings.gemini_api_key)

        model = genai.GenerativeModel(
            model_name=settings.gemini_model_generate,
            generation_config=genai.GenerationConfig(
                temperature=settings.gemini_temperature_generate,
                top_p=0.8,
                response_mime_type="application/json",
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            },
        )

        prompt = self._build_prompt(concept_name, concept_code, grade_level, age, count)

        response = await asyncio.to_thread(model.generate_content, prompt)

        raw = response.text.strip()
        # Retirer éventuels blocs markdown ```json ... ```
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        data = json.loads(raw)
        if isinstance(data, dict) and "exercises" in data:
            data = data["exercises"]
        if not isinstance(data, list):
            raise ValueError(f"Réponse Gemini inattendue : {type(data)}")

        exercises: list[GeneratedExercise] = []
        for item in data[:count]:
            ex_type_str = str(item.get("type", "mcq")).lower()
            try:
                ex_type = ExerciseType(ex_type_str)
            except ValueError:
                ex_type = ExerciseType.MCQ

            exercises.append(
                GeneratedExercise(
                    type=ex_type,
                    prompt=str(item.get("prompt", "")),
                    options=item.get("options") if ex_type == ExerciseType.MCQ else None,
                    correct_answer=str(item.get("correct_answer", "")),
                    explanation_short=str(item.get("explanation_short", ""))[:120],
                    tts_text=item.get("tts_text"),
                    difficulty=min(max(int(item.get("difficulty", 2)), 1), 4),
                )
            )

        logger.info(
            "gemini.exercises_generated",
            concept_code=concept_code,
            requested=count,
            received=len(exercises),
            model=settings.gemini_model_generate,
        )
        return exercises

    def _build_prompt(
        self,
        concept_name: str,
        concept_code: str,
        grade_level: str,
        age: int,
        count: int,
    ) -> str:
        return f"""Tu es un professeur comorien expert en pédagogie APC (Approche par Compétences).

Génère exactement {count} micro-exercices de remédiation sur le concept : "{concept_name}" (code: {concept_code}).
Niveau : {grade_level}, élève de {age} ans.

RÈGLES ABSOLUES :
1. Prénoms autorisés : Ali, Fatima, Said, Mariama, Omar, Nassima, Khalid, Aïcha
2. Monnaie : KMF uniquement (jamais €, $, F CFA)
3. Contexte : vie quotidienne comorienne (marché, pêche, école, famille, île)
4. Phrases : ≤ 15 mots par phrase
5. Vocabulaire : adapté à {age} ans, simple et direct
6. Varier les types : priorité "mcq", puis "fill_blank", puis "short_text"
7. Difficulté croissante : exercice 1 = facile, exercice {count} = difficile

Retourne UNIQUEMENT un tableau JSON valide avec {count} objets :
[
  {{
    "type": "mcq",
    "prompt": "string — question ou consigne (≤ 15 mots)",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "correct_answer": "A) ...",
    "explanation_short": "string (≤ 10 mots)",
    "tts_text": "string — phrase complète pour lecture TTS",
    "difficulty": 1
  }}
]
Pour fill_blank et short_text, mets options à null."""

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
