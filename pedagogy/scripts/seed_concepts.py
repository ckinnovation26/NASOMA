"""Seed les concepts pédagogiques depuis les JSON vers PostgreSQL.

Usage :
    py pedagogy/scripts/seed_concepts.py

Prérequis : DATABASE_URL dans l'env ou un fichier .env à la racine du backend.
"""

from __future__ import annotations

import asyncio
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.concepts import Concept, ConceptPrerequisite
from app.models.subjects import Subject

CURRICULUM_DIR = Path(__file__).parent.parent / "apc_km"

SUBJECT_CODES = {
    "MATH": {"name": "Mathématiques", "locale": "fr-KM"},
    "FR":   {"name": "Français",      "locale": "fr-KM"},
    "AR":   {"name": "Arabe",         "locale": "ar-KM"},
    "SCI":  {"name": "Sciences",      "locale": "fr-KM"},
}


async def get_or_create_subject(session: AsyncSession, code: str, grade_level: str) -> Subject:
    result = await session.execute(
        select(Subject).where(Subject.code == code, Subject.grade_level == grade_level)
    )
    subject = result.scalar_one_or_none()
    if subject is None:
        info = SUBJECT_CODES[code]
        subject = Subject(
            id=uuid.uuid4(),
            code=code,
            name=info["name"],
            grade_level=grade_level,
            locale=info["locale"],
        )
        session.add(subject)
        await session.flush()
    return subject


async def seed_file(session: AsyncSession, json_path: Path) -> int:
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)

    meta = data["metadata"]
    subject = await get_or_create_subject(session, meta["subject"], meta["grade_level"])

    code_to_id: dict[str, uuid.UUID] = {}
    inserted = 0

    for c in data.get("concepts", []):
        result = await session.execute(select(Concept).where(Concept.code == c["code"]))
        existing = result.scalar_one_or_none()
        if existing:
            code_to_id[c["code"]] = existing.id
            continue

        concept = Concept(
            id=uuid.uuid4(),
            subject_id=subject.id,
            code=c["code"],
            name=c["name"],
            name_shikomori=c.get("name_shikomori"),
            grade_level=meta["grade_level"],
            difficulty=c["difficulty"],
            estimated_minutes=c.get("estimated_minutes"),
            description=c.get("description"),
            curriculum_refs=c.get("curriculum_refs"),
            common_errors=c.get("common_errors", []),
        )
        session.add(concept)
        await session.flush()
        code_to_id[c["code"]] = concept.id
        inserted += 1

    for c in data.get("concepts", []):
        for prereq_code in c.get("prerequisites", []):
            if prereq_code not in code_to_id:
                continue
            result = await session.execute(
                select(ConceptPrerequisite).where(
                    ConceptPrerequisite.concept_id == code_to_id[c["code"]],
                    ConceptPrerequisite.prerequisite_id == code_to_id[prereq_code],
                )
            )
            if result.scalar_one_or_none() is None:
                session.add(ConceptPrerequisite(
                    concept_id=code_to_id[c["code"]],
                    prerequisite_id=code_to_id[prereq_code],
                ))

    return inserted


async def main() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    total = 0
    async with maker() as session:
        for json_file in sorted(CURRICULUM_DIR.glob("*.json")):
            n = await seed_file(session, json_file)
            print(f"  {json_file.name} → {n} concept(s) insérés")
            total += n
        await session.commit()

    await engine.dispose()
    print(f"\n✅ Seed terminé — {total} concept(s) ajoutés au total.")


if __name__ == "__main__":
    asyncio.run(main())
