"""Client Firestore — écritures temps réel (quotas, cache scan, sessions chaudes)."""

import os
from functools import lru_cache

from google.cloud import firestore

from app.core.config import settings


@lru_cache(maxsize=1)
def get_firestore_client() -> firestore.AsyncClient:
    """Singleton client Firestore async.

    Utilise l'émulateur si FIRESTORE_EMULATOR_HOST est défini.
    """
    if settings.firestore_emulator_host:
        os.environ["FIRESTORE_EMULATOR_HOST"] = settings.firestore_emulator_host

    return firestore.AsyncClient(project=settings.firestore_project_id)
