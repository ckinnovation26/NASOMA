"""Service ConceptMapper — mappe une erreur détectée vers un concept_code APC_KM.

Utilise Gemini Flash-8B avec grounding strict : la liste des concept_codes
autorisés est passée en contexte. Toute génération avec un code hors liste
est rejetée (validation post-LLM, cf. anti-hallucination §24 BP).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.concepts import Concept
from app.models.subjects import Subject

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class ConceptMapping:
    """Résultat du mapping IA."""

    concept_code: str
    concept_id: uuid.UUID
    error_category: str       # 'calculation_mistake' | 'logic_gap' | 'rule_forgotten' | 'conceptual_misunderstanding'
    confidence: float
    cost_usd: float


class ConceptMapperService:
    """Mappe une erreur extraite par OCR vers un concept du Knowledge Graph."""

    VALID_ERROR_CATEGORIES = (
        "calculation_mistake",
        "logic_gap",
        "rule_forgotten",
        "conceptual_misunderstanding",
    )

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def map_error(
        self,
        error_description: str,
        statement: str,
        grade_level: str,
        subject_code: str,
        curriculum_code: str = "APC_KM",
    ) -> ConceptMapping | None:
        """Mappe une erreur vers un concept_code.

        1. Récupère la whitelist des concept_codes éligibles
        2. Appelle Gemini avec la whitelist en grounding strict
        3. Valide que le code retourné existe bien dans la whitelist
        4. Retourne None si pas de mapping fiable (confidence < 0.6)
        """
        whitelist = await self._get_whitelist(grade_level, subject_code)
        if not whitelist:
            logger.warning(
                "concept_mapper.empty_whitelist",
                grade=grade_level,
                subject=subject_code,
            )
            return None

        # Appel Gemini (stub dev)
        try:
            raw = await self._call_gemini(
                error_description=error_description,
                statement=statement,
                grade_level=grade_level,
                subject_code=subject_code,
                curriculum_code=curriculum_code,
                concept_codes_whitelist=list(whitelist.keys()),
            )
        except NotImplementedError:
            # Sprint 2 stub — pick the first concept of the whitelist
            if not whitelist:
                return None
            code, concept_id = next(iter(whitelist.items()))
            return ConceptMapping(
                concept_code=code,
                concept_id=concept_id,
                error_category="calculation_mistake",
                confidence=0.7,
                cost_usd=0.0,
            )

        code = raw.get("concept_code")
        category = raw.get("error_category")
        confidence = float(raw.get("confidence", 0.0))
        cost_usd = float(raw.get("cost_usd", 0.0))

        # Validation post-LLM (anti-hallucination)
        if code not in whitelist:
            logger.warning(
                "concept_mapper.hallucinated_code",
                returned=code,
                grade=grade_level,
                subject=subject_code,
            )
            return None
        if category not in self.VALID_ERROR_CATEGORIES:
            category = "calculation_mistake"
        if confidence < 0.6:
            logger.info("concept_mapper.low_confidence", code=code, confidence=confidence)
            return None

        return ConceptMapping(
            concept_code=code,
            concept_id=whitelist[code],
            error_category=category,
            confidence=confidence,
            cost_usd=cost_usd,
        )

    # ──────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────
    async def _get_whitelist(
        self,
        grade_level: str,
        subject_code: str,
    ) -> dict[str, uuid.UUID]:
        """Récupère { concept_code: concept_id } pour le grade + matière."""
        stmt = (
            select(Concept.code, Concept.id)
            .join(Subject, Subject.id == Concept.subject_id)
            .where(Subject.code == subject_code, Concept.grade_level == grade_level)
        )
        result = await self.db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}

    async def _call_gemini(
        self,
        error_description: str,
        statement: str,
        grade_level: str,
        subject_code: str,
        curriculum_code: str,
        concept_codes_whitelist: list[str],
    ) -> dict:
        """Appel Gemini Flash-8B avec responseSchema strict.

        Prompt cf. §24 BP "Prompt 2 — Mapping concept (texte LLM)".
        À implémenter Sprint 2.5.
        """
        if settings.app_env == "dev" and not settings.gemini_api_key:
            raise NotImplementedError("Gemini mapping à implémenter Sprint 2.5 (stub dev)")

        # Implémentation réelle (Sprint 2.5)
        # import google.generativeai as genai
        # genai.configure(api_key=settings.gemini_api_key)
        # model = genai.GenerativeModel(
        #     settings.gemini_model_generate,
        #     generation_config={
        #         "temperature": 0.0,
        #         "response_mime_type": "application/json",
        #         "response_schema": SCHEMA_CONCEPT_MAPPING,
        #     },
        # )
        # prompt = f"...{concept_codes_whitelist}..."
        # response = await model.generate_content_async(prompt)
        # return json.loads(response.text)

        raise NotImplementedError("Gemini mapping à implémenter Sprint 2.5")
