"""Service OCR — pipeline 3 étages (cf. docs/architecture.md).

Étage 1 : ML Kit on-device (gratuit, on reçoit le résultat dans le payload mobile)
Étage 2 : Google Cloud Vision Document Text Detection (~0,0015 $/page)
Étage 3 : Gemini 2.0 Flash vision (cas vraiment difficiles)

Bascule :
- Si étage 1 confidence > 0.85 → on garde ce résultat
- Sinon → étage 2
- Si étage 2 confidence > 0.70 → on garde
- Sinon → étage 3
- Si étage 3 < FALLBACK_CONFIDENCE_THRESHOLD → fallback "Always Give Value"
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

from app.core.config import settings
from app.models.scans import OcrProvider

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class OcrResult:
    """Résultat brut OCR."""

    text: str
    confidence: float
    provider: OcrProvider
    cost_usd: float
    needs_fallback: bool


@dataclass(frozen=True)
class MlkitResult:
    """Résultat ML Kit envoyé par le client mobile."""

    text: str
    confidence: float


class OcrService:
    """Orchestrateur du pipeline 3 étages."""

    THRESHOLD_MLKIT_OK = 0.85
    THRESHOLD_VISION_OK = 0.70

    async def run(
        self,
        image_bytes: bytes,
        mlkit_result: MlkitResult | None = None,
    ) -> OcrResult:
        """Lance le pipeline OCR avec bascules conditionnelles.

        Returns:
            OcrResult avec text + confidence + provider + coût.
            needs_fallback=True si même l'étage 3 n'a pas confiance suffisante.
        """
        # ─── Étage 1 — ML Kit local (gratuit) ───
        if mlkit_result and mlkit_result.confidence >= self.THRESHOLD_MLKIT_OK:
            logger.info("ocr.stage1_mlkit_sufficient", confidence=mlkit_result.confidence)
            return OcrResult(
                text=mlkit_result.text,
                confidence=mlkit_result.confidence,
                provider=OcrProvider.MLKIT_LOCAL,
                cost_usd=0.0,
                needs_fallback=False,
            )

        # ─── Étage 2 — Google Cloud Vision ───
        try:
            vision_result = await self._call_cloud_vision(image_bytes)
            if vision_result.confidence >= self.THRESHOLD_VISION_OK:
                logger.info(
                    "ocr.stage2_vision_sufficient",
                    confidence=vision_result.confidence,
                )
                return vision_result
        except Exception as e:
            logger.warning("ocr.stage2_vision_failed", error=str(e))
            vision_result = None

        # ─── Étage 3 — Gemini Flash vision ───
        try:
            gemini_result = await self._call_gemini_vision(image_bytes)
            needs_fallback = (
                gemini_result.confidence < settings.fallback_confidence_threshold
            )
            return OcrResult(
                text=gemini_result.text,
                confidence=gemini_result.confidence,
                provider=OcrProvider.GEMINI_FLASH,
                cost_usd=gemini_result.cost_usd,
                needs_fallback=needs_fallback,
            )
        except Exception as e:
            logger.error("ocr.stage3_gemini_failed", error=str(e))

        # Tous les étages ont échoué → fallback
        return OcrResult(
            text="",
            confidence=0.0,
            provider=OcrProvider.GEMINI_FLASH,
            cost_usd=0.0,
            needs_fallback=True,
        )

    # ──────────────────────────────────────────────
    #  Étage 2 — Google Cloud Vision (à implémenter Sprint 2.5)
    # ──────────────────────────────────────────────
    async def _call_cloud_vision(self, image_bytes: bytes) -> OcrResult:
        """Appel Google Cloud Vision Document Text Detection.

        TODO: implémenter avec `google-cloud-vision` SDK.
        Pour Sprint 2 — stub qui simule un appel.
        """
        if settings.app_env == "dev" and not settings.vision_api_enabled:
            # Stub dev — return low confidence pour forcer l'étage 3
            return OcrResult(
                text="[stub vision text]",
                confidence=0.5,
                provider=OcrProvider.CLOUD_VISION,
                cost_usd=0.0015,
                needs_fallback=False,
            )

        # Implémentation réelle (Sprint 2.5)
        # from google.cloud import vision
        # client = vision.ImageAnnotatorClient()
        # image = vision.Image(content=image_bytes)
        # response = client.document_text_detection(image=image)
        # ...

        raise NotImplementedError("Cloud Vision appel à implémenter Sprint 2.5")

    # ──────────────────────────────────────────────
    #  Étage 3 — Gemini 2.0 Flash Vision
    # ──────────────────────────────────────────────
    async def _call_gemini_vision(self, image_bytes: bytes) -> OcrResult:
        """Appel Gemini 2.0 Flash vision pour OCR + interprétation.

        TODO: implémenter avec `google-generativeai` SDK.
        Pour Sprint 2 — stub qui simule un appel.
        """
        if settings.app_env == "dev" and not settings.gemini_api_key:
            return OcrResult(
                text="[stub gemini vision text]",
                confidence=0.75,
                provider=OcrProvider.GEMINI_FLASH,
                cost_usd=0.005,
                needs_fallback=False,
            )

        # Implémentation réelle (Sprint 2.5)
        # import google.generativeai as genai
        # genai.configure(api_key=settings.gemini_api_key)
        # model = genai.GenerativeModel(settings.gemini_model_extract)
        # response = await model.generate_content_async([
        #     "Tu es un assistant OCR pour copies d'élèves...",
        #     {"mime_type": "image/jpeg", "data": image_bytes}
        # ])
        # ...

        raise NotImplementedError("Gemini Vision appel à implémenter Sprint 2.5")
