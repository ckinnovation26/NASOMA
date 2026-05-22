"""Tests unitaires service OTP — génération, vérification, rotation, expiration."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.otp_challenges import OtpStatus, OtpType
from app.models.tenants import Tenant
from app.services.otp_service import (
    OtpExpiredError,
    OtpInvalidError,
    OtpMaxAttemptsError,
    OtpService,
)


@pytest.fixture
async def tenant(db_session: AsyncSession) -> Tenant:
    tenant = Tenant(
        code="KM",
        name="Union des Comores",
        default_locale="fr-KM",
        currency="KMF",
    )
    db_session.add(tenant)
    await db_session.flush()
    return tenant


@pytest.mark.integration
async def test_create_sms_first_signup_generates_otp(db_session: AsyncSession, tenant: Tenant) -> None:
    svc = OtpService(db_session)
    challenge, code = await svc.create_sms_first_signup(
        tenant_id=tenant.id,
        phone="+26934125678",
    )

    assert challenge.id is not None
    assert challenge.otp_type == OtpType.SMS_FIRST_SIGNUP
    assert challenge.status == OtpStatus.PENDING
    assert len(code) == 6
    assert code.isdigit()


@pytest.mark.integration
async def test_verify_consume_success(db_session: AsyncSession, tenant: Tenant) -> None:
    svc = OtpService(db_session)
    _, code = await svc.create_sms_first_signup(tenant_id=tenant.id, phone="+26934125678")

    consumed = await svc.verify_and_consume(phone="+26934125678", code=code)
    assert consumed.status == OtpStatus.CONSUMED
    assert consumed.consumed_at is not None


@pytest.mark.integration
async def test_verify_wrong_code_increments_attempts(
    db_session: AsyncSession, tenant: Tenant
) -> None:
    svc = OtpService(db_session)
    challenge, _ = await svc.create_sms_first_signup(
        tenant_id=tenant.id, phone="+26934125678"
    )

    with pytest.raises(OtpInvalidError):
        await svc.verify_and_consume(phone="+26934125678", code="000000")

    await db_session.refresh(challenge)
    assert challenge.attempts == 1
    assert challenge.status == OtpStatus.PENDING


@pytest.mark.integration
async def test_max_attempts_invalidates(db_session: AsyncSession, tenant: Tenant) -> None:
    svc = OtpService(db_session)
    challenge, _ = await svc.create_sms_first_signup(
        tenant_id=tenant.id, phone="+26934125678"
    )
    challenge.max_attempts = 2
    await db_session.flush()

    with pytest.raises(OtpInvalidError):
        await svc.verify_and_consume(phone="+26934125678", code="000000")
    with pytest.raises(OtpInvalidError):
        await svc.verify_and_consume(phone="+26934125678", code="000001")
    with pytest.raises(OtpMaxAttemptsError):
        await svc.verify_and_consume(phone="+26934125678", code="000002")


@pytest.mark.integration
async def test_expired_otp_raises(db_session: AsyncSession, tenant: Tenant) -> None:
    svc = OtpService(db_session)
    challenge, code = await svc.create_sms_first_signup(
        tenant_id=tenant.id, phone="+26934125678"
    )
    challenge.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    await db_session.flush()

    with pytest.raises(OtpExpiredError):
        await svc.verify_and_consume(phone="+26934125678", code=code)


@pytest.mark.integration
async def test_rotation_invalidates_previous_otp(
    db_session: AsyncSession, tenant: Tenant
) -> None:
    """Un nouvel OTP rend les anciens invalidés (rotation = sécurité)."""
    svc = OtpService(db_session)
    old, old_code = await svc.create_sms_first_signup(
        tenant_id=tenant.id, phone="+26934125678"
    )
    _, _ = await svc.create_sms_first_signup(tenant_id=tenant.id, phone="+26934125678")

    await db_session.refresh(old)
    assert old.status == OtpStatus.INVALIDATED

    # L'ancien code ne marche plus
    with pytest.raises(OtpInvalidError):
        await svc.verify_and_consume(phone="+26934125678", code=old_code)


@pytest.mark.integration
async def test_vendor_ticket_otp_has_long_ttl(
    db_session: AsyncSession, tenant: Tenant
) -> None:
    """OTP ticket vendeur = durée du crédit (24h / 7j / 30j)."""
    svc = OtpService(db_session)
    challenge, _ = await svc.create_vendor_ticket(
        tenant_id=tenant.id,
        phone="+26934125678",
        subscription_id=uuid.uuid4(),
        recharge_ticket_code="NSMA-A3F2-9B1C-7D4E",
        duration_days=30,
    )
    delta = challenge.expires_at - datetime.now(UTC).replace(tzinfo=challenge.expires_at.tzinfo)
    assert delta.days == 29 or delta.days == 30
    assert challenge.otp_type == OtpType.VENDOR_TICKET
