"""Nasoma — point d'entrée FastAPI.

Lance: uvicorn app.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.logging import configure_logging

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    configure_logging()
    logger.info("nasoma.startup", env=settings.app_env, version=__version__)
    yield
    logger.info("nasoma.shutdown")


app = FastAPI(
    title="Nasoma API",
    description="Backend de l'app EdTech Nasoma — *Mimi, Nasoma.*",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs" if settings.app_env != "prod" else None,
    redoc_url="/redoc" if settings.app_env != "prod" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Liveness probe pour Cloud Run."""
    return {"status": "ok", "version": __version__, "env": settings.app_env}


app.include_router(api_v1_router, prefix="/api/v1")
