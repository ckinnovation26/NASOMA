"""Fixtures Pytest partagées."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.db.session import Base
from app.main import app


@pytest.fixture(scope="session")
def database_url() -> str:
    """URL Postgres test (utilise un schéma/db séparée idéalement)."""
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://nasoma:testpass@localhost:5432/nasoma_test",
    )


@pytest.fixture(scope="session")
async def engine(database_url: str):
    engine = create_async_engine(database_url, poolclass=NullPool, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Session DB par test avec rollback automatique."""
    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def client() -> TestClient:
    """Client HTTP synchrone pour smoke tests rapides."""
    return TestClient(app)
