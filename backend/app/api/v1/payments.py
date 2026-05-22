"""Endpoints paiements — initiate + webhook par provider."""

from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.payments import Payment
from app.models.subscriptions import SubscriptionPlan
from app.models.tenants import Tenant
from app.schemas.payments import (
    PaymentDetailResponse,
    PaymentInitiatePayload,
    PaymentInitiateResponse,
)
from app.services.payment_service import PaymentService

logger = structlog.get_logger(__name__)

router = APIRouter()


async def _default_tenant_id(db: AsyncSession) -> uuid.UUID:
    result = await db.execute(select(Tenant.id).where(Tenant.code == "KM"))
    tenant_id = result.scalar_one_or_none()
    if tenant_id is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Tenant KM introuvable."
        )
    return tenant_id


# ──────────────────────────────────────────────
#  POST /payments/initiate
# ──────────────────────────────────────────────
@router.post(
    "/initiate",
    response_model=PaymentInitiateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initier un paiement (STK push Hollo/Mvola, Stripe Checkout, ou vendeur cash)",
)
async def initiate_payment(
    payload: PaymentInitiatePayload,
    db: AsyncSession = Depends(get_db),
) -> PaymentInitiateResponse:
    tenant_id = await _default_tenant_id(db)
    svc = PaymentService(db)

    plan_map = {
        "daily": SubscriptionPlan.DAILY,
        "three_day": SubscriptionPlan.THREE_DAY,
        "weekly": SubscriptionPlan.WEEKLY,
        "monthly": SubscriptionPlan.MONTHLY_PER_CHILD,
    }
    plan = plan_map.get(payload.plan)
    if plan is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Plan inconnu: {payload.plan}")

    try:
        result = await svc.initiate(
            user_id=payload.user_id,
            tenant_id=tenant_id,
            plan=plan,
            provider_code=payload.provider,
            vendor_id=payload.vendor_code,
            school_id=payload.school_id,
        )
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e

    await db.commit()
    return PaymentInitiateResponse(
        payment_id=result.payment_id,
        provider_ref=result.provider_ref,
        user_action_text=result.user_action_text,
        ussd_code=result.ussd_code,
        redirect_url=result.redirect_url,
        expires_in_seconds=result.expires_in_seconds,
    )


# ──────────────────────────────────────────────
#  POST /payments/webhook/{provider}
# ──────────────────────────────────────────────
@router.post(
    "/webhook/hollo",
    summary="Webhook Hollo — confirme paiement → active subscription + OTP ticket",
)
async def webhook_hollo(
    request: Request,
    x_hollo_signature: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    payload = await request.json()
    svc = PaymentService(db)
    payment = await svc.handle_webhook("hollo", payload, x_hollo_signature)
    await db.commit()
    if payment is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Webhook invalide.")
    return {
        "payment_id": str(payment.id),
        "status": payment.status.value
        if hasattr(payment.status, "value")
        else str(payment.status),
    }


@router.post(
    "/webhook/mvola",
    summary="Webhook Mvola",
)
async def webhook_mvola(
    request: Request,
    x_mvola_signature: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    payload = await request.json()
    svc = PaymentService(db)
    payment = await svc.handle_webhook("mvola", payload, x_mvola_signature)
    await db.commit()
    if payment is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Webhook invalide.")
    return {"payment_id": str(payment.id), "status": payment.status.value}


@router.post(
    "/webhook/stripe",
    summary="Webhook Stripe (diaspora)",
)
async def webhook_stripe(
    request: Request,
    stripe_signature: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    payload = await request.json()
    svc = PaymentService(db)
    payment = await svc.handle_webhook("stripe", payload, stripe_signature)
    await db.commit()
    if payment is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Webhook invalide.")
    return {"payment_id": str(payment.id), "status": payment.status.value}


# ──────────────────────────────────────────────
#  GET /payments/{id}
# ──────────────────────────────────────────────
@router.get(
    "/{payment_id}",
    response_model=PaymentDetailResponse,
    summary="Détail d'un paiement",
)
async def get_payment(
    payment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PaymentDetailResponse:
    payment = await db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Paiement introuvable.")

    return PaymentDetailResponse(
        payment_id=payment.id,
        status=payment.status.value if hasattr(payment.status, "value") else str(payment.status),
        amount_local=float(payment.amount_local),
        currency=payment.currency,
        provider=payment.provider.value if hasattr(payment.provider, "value") else str(payment.provider),
        provider_ref=payment.provider_ref,
        created_at=payment.created_at,
        completed_at=payment.completed_at,
    )
