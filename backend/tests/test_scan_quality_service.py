"""Tests ScanQuality — détection de récurrence + extraction keywords."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scans import Scan, ScanStatus
from app.models.tenants import Tenant
from app.models.users import User, UserRole
from app.services.scan_quality_service import ScanQualityService


@pytest.fixture
async def setup(db_session: AsyncSession):
    tenant = Tenant(
        code="KM",
        name="Comores",
        default_locale="fr-KM",
        currency="KMF",
    )
    db_session.add(tenant)
    await db_session.flush()
    user = User(
        tenant_id=tenant.id,
        phone="+26934000001",
        role=UserRole.STUDENT,
    )
    db_session.add(user)
    await db_session.flush()
    return tenant, user


@pytest.mark.integration
async def test_no_failed_scans_should_not_propose_assistance(
    db_session: AsyncSession, setup
) -> None:
    tenant, user = setup
    svc = ScanQualityService(db_session)
    assert await svc.count_failed_scans_last_7d(user.id) == 0
    assert not await svc.should_propose_assistance(user.id)


@pytest.mark.integration
async def test_3_fallback_scans_in_7d_triggers_assistance(
    db_session: AsyncSession, setup
) -> None:
    tenant, user = setup
    now = datetime.now(UTC)
    for i in range(3):
        scan = Scan(
            tenant_id=tenant.id,
            student_id=user.id,
            image_storage_key=f"key-{i}",
            status=ScanStatus.DONE_WITH_FALLBACK,
            fallback_used=True,
            created_at=now - timedelta(days=i),
        )
        db_session.add(scan)
    await db_session.flush()

    svc = ScanQualityService(db_session)
    assert await svc.count_failed_scans_last_7d(user.id) == 3
    assert await svc.should_propose_assistance(user.id)


@pytest.mark.integration
async def test_old_failed_scans_dont_count(db_session: AsyncSession, setup) -> None:
    tenant, user = setup
    old = datetime.now(UTC) - timedelta(days=30)
    for i in range(5):
        scan = Scan(
            tenant_id=tenant.id,
            student_id=user.id,
            image_storage_key=f"key-{i}",
            status=ScanStatus.DONE_WITH_FALLBACK,
            created_at=old,
        )
        db_session.add(scan)
    await db_session.flush()

    svc = ScanQualityService(db_session)
    assert await svc.count_failed_scans_last_7d(user.id) == 0


def test_extract_keywords_basic() -> None:
    out = ScanQualityService.extract_keywords(
        "Mon enfant a des difficultés avec les multiplications à 2 chiffres"
    )
    assert out is not None
    assert "multiplications" in out


def test_extract_keywords_empty_returns_none() -> None:
    assert ScanQualityService.extract_keywords(None) is None
    assert ScanQualityService.extract_keywords("") is None
