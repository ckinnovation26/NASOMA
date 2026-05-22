"""Service pHash — hash perceptuel anti-rescan.

Si le même devoir est rescanné dans les 24h, on retourne le diagnostic en cache
SANS décrémenter le quota (cf. anti-abus mécanisme #2 dans docs/pricing.md).
"""

from __future__ import annotations

import io
import uuid

import imagehash
import structlog
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.scans import Scan, ScanStatus

logger = structlog.get_logger(__name__)


def compute_phash(image_bytes: bytes) -> str:
    """Calcule un hash perceptuel 64 bits depuis les bytes d'une image."""
    with Image.open(io.BytesIO(image_bytes)) as img:
        phash = imagehash.phash(img, hash_size=8)
    return str(phash)


def hamming_distance(hash_a: str, hash_b: str) -> int:
    """Distance de Hamming entre deux hashes hex (16 chars = 64 bits)."""
    if len(hash_a) != len(hash_b):
        return 64
    a = int(hash_a, 16)
    b = int(hash_b, 16)
    return bin(a ^ b).count("1")


class PhashService:
    """Détecte les scans en double dans les 24h."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def find_cached_scan(
        self,
        student_id: uuid.UUID,
        new_phash: str,
        max_hamming_distance: int = 5,
    ) -> Scan | None:
        """Cherche un scan récent (< TTL) avec un pHash similaire.

        Tolérance pHash : 5 bits de différence (sur 64) = très proche visuellement.
        """
        cutoff_hours = settings.quota_phash_cache_ttl_hours

        stmt = (
            select(Scan)
            .where(
                Scan.student_id == student_id,
                Scan.status.in_([ScanStatus.DONE, ScanStatus.DONE_WITH_FALLBACK]),
                Scan.image_phash.isnot(None),
                # Cutoff par interval — laisse SQLAlchemy gérer le timezone
                Scan.created_at >= __import__("datetime").datetime.utcnow().replace(
                    microsecond=0
                ).__sub__(__import__("datetime").timedelta(hours=cutoff_hours)),
            )
            .order_by(Scan.created_at.desc())
            .limit(20)                                    # on en regarde 20 récents
        )
        result = await self.db.execute(stmt)
        candidates = result.scalars().all()

        for candidate in candidates:
            if candidate.image_phash is None:
                continue
            distance = hamming_distance(new_phash, candidate.image_phash)
            if distance <= max_hamming_distance:
                logger.info(
                    "phash.cache_hit",
                    student=str(student_id),
                    cached_scan=str(candidate.id),
                    distance=distance,
                )
                return candidate

        return None
