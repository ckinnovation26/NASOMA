"""Script dev — crée toutes les tables SQLAlchemy directement.

Usage :
    py backend/scripts/create_tables.py

Utiliser UNIQUEMENT en dev local. En prod, utiliser alembic upgrade head.
"""

import asyncio
import sys
from pathlib import Path

# Permet d'importer app.* depuis la racine du backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import Base, engine
from app.models import *  # noqa: F401, F403 — enregistre tous les modèles dans Base.metadata


async def create_all() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"Tables créées : {sorted(Base.metadata.tables.keys())}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_all())
