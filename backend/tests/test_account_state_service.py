"""Tests state machine compte — transitions active → grace → frozen → archived."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenants import Tenant
from app.models.users import AccountState, User, UserRole
from app.services.account_state_service import AccountStateService


@pytest.fixture
async def tenant(db_session: AsyncSession) -> Tenant:
    tenant = Tenant(
        code="KM",
        name="Comores",
        default_locale="fr-KM",
        currency="KMF",
    )
    db_session.add(tenant)
    await db_session.flush()
    return tenant


async def _make_user(
    db: AsyncSession, tenant: Tenant, state: AccountState, expires_at: datetime
) -> User:
    user = User(
        tenant_id=tenant.id,
        phone=f"+269{datetime.now().microsecond:08d}",
        role=UserRole.STUDENT,
        account_state=state,
        credit_expires_at=expires_at,
        first_signup_phone_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


@pytest.mark.integration
async def test_active_user_stays_active(db_session: AsyncSession, tenant: Tenant) -> None:
    user = await _make_user(
        db_session, tenant, AccountState.ACTIVE, datetime.now(UTC) + timedelta(days=15)
    )
    svc = AccountStateService(db_session)
    info = await svc.get_info(user.id)
    assert info.state == AccountState.ACTIVE
    assert info.can_perform_new_actions
    assert not info.paywall_required


@pytest.mark.integration
async def test_active_transitions_to_grace_when_expired(
    db_session: AsyncSession, tenant: Tenant
) -> None:
    user = await _make_user(
        db_session, tenant, AccountState.ACTIVE, datetime.now(UTC) - timedelta(days=5)
    )
    svc = AccountStateService(db_session)
    info = await svc.get_info(user.id)
    assert info.state == AccountState.GRACE
    assert info.can_read_data
    assert not info.can_perform_new_actions
    assert info.days_remaining_grace is not None
    assert info.days_remaining_grace < 30


@pytest.mark.integration
async def test_grace_transitions_to_frozen_after_30j(
    db_session: AsyncSession, tenant: Tenant
) -> None:
    user = await _make_user(
        db_session, tenant, AccountState.GRACE, datetime.now(UTC) - timedelta(days=35)
    )
    svc = AccountStateService(db_session)
    info = await svc.get_info(user.id)
    assert info.state == AccountState.FROZEN
    assert not info.can_login_direct
    assert not info.can_read_data


@pytest.mark.integration
async def test_frozen_transitions_to_archived_after_365j(
    db_session: AsyncSession, tenant: Tenant
) -> None:
    user = await _make_user(
        db_session, tenant, AccountState.FROZEN, datetime.now(UTC) - timedelta(days=400)
    )
    svc = AccountStateService(db_session)
    info = await svc.get_info(user.id)
    assert info.state == AccountState.ARCHIVED


@pytest.mark.integration
async def test_cron_transitions_all_due(db_session: AsyncSession, tenant: Tenant) -> None:
    """Cron bulk transitions."""
    await _make_user(
        db_session, tenant, AccountState.ACTIVE, datetime.now(UTC) - timedelta(days=1)
    )
    await _make_user(
        db_session, tenant, AccountState.ACTIVE, datetime.now(UTC) - timedelta(days=2)
    )
    await _make_user(
        db_session, tenant, AccountState.GRACE, datetime.now(UTC) - timedelta(days=40)
    )

    svc = AccountStateService(db_session)
    counts = await svc.transition_all_due()
    assert counts["active_to_grace"] >= 2
    assert counts["grace_to_frozen"] >= 1
