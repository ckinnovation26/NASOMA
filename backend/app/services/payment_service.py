"""PaymentService — orchestration paiement + création Subscription + OtpChallenge ticket.

Gère le cycle complet :
1. Création Payment (status=PENDING)
2. Appel provider.initiate()
3. Webhook → verify → marquer SUCCESS
4. Sur SUCCESS : créer Subscription + OtpChallenge VENDOR_TICKET + grant_credits Firestore
"""

from __future__ import annotations

import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_otp, hash_otp
from app.models.otp_challenges import OtpChallenge, OtpStatus, OtpType
from app.models.payments import Payment, PaymentProvider, PaymentStatus
from app.models.subscriptions import (
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
)
from app.models.users import AccountState, User
from app.services.payments import get_provider
from app.services.quota_service import QuotaService

logger = structlog.get_logger(__name__)


# Tarifs verrouillés business (cf. docs/pricing.md)
PLAN_PRICING_KMF = {
    SubscriptionPlan.DAILY: 100,
    SubscriptionPlan.THREE_DAY: 250,
    SubscriptionPlan.WEEKLY: 500,
    SubscriptionPlan.MONTHLY_PER_CHILD: 1500,
}
PLAN_SCANS = {
    SubscriptionPlan.DAILY: 5,
    SubscriptionPlan.THREE_DAY: 15,
    SubscriptionPlan.WEEKLY: 30,
    SubscriptionPlan.MONTHLY_PER_CHILD: 120,
}
PLAN_DURATION_DAYS = {
    SubscriptionPlan.DAILY: 1,
    SubscriptionPlan.THREE_DAY: 3,
    SubscriptionPlan.WEEKLY: 7,
    SubscriptionPlan.MONTHLY_PER_CHILD: 30,
}


@dataclass(frozen=True)
class PaymentInitiationResult:
    """Résultat d'une initiation côté Nasoma."""

    payment_id: uuid.UUID
    provider_ref: str
    user_action_text: str | None
    ussd_code: str | None
    redirect_url: str | None
    expires_in_seconds: int


class PaymentService:
    """Orchestration paiement + activation subscription + OTP ticket."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def initiate(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        plan: SubscriptionPlan,
        provider_code: str,
        vendor_id: str | None = None,
        school_id: uuid.UUID | None = None,
    ) -> PaymentInitiationResult:
        """Initie un paiement pour un plan donné."""
        user = await self.db.get(User, user_id)
        if user is None:
            raise ValueError("User not found")

        if plan not in PLAN_PRICING_KMF:
            raise ValueError(f"Plan invalide pour initiation: {plan}")
        amount = PLAN_PRICING_KMF[plan]

        # Mapper provider_code → enum
        provider_enum_map = {
            "hollo": PaymentProvider.HOLLO,
            "mvola": PaymentProvider.MVOLA,
            "stripe": PaymentProvider.STRIPE,
            "physical_ticket": PaymentProvider.PHYSICAL_TICKET,
            "school_b2b": PaymentProvider.SCHOOL_B2B,
        }
        provider_enum = provider_enum_map.get(provider_code.lower())
        if provider_enum is None:
            raise ValueError(f"Provider inconnu: {provider_code}")

        # Créer Payment en status PENDING
        payment = Payment(
            tenant_id=tenant_id,
            user_id=user_id,
            amount_local=amount,
            currency="KMF",
            provider=provider_enum,
            status=PaymentStatus.PENDING,
            vendor_id=vendor_id,
            school_id=school_id,
            notes=f"Plan: {plan.value}",
        )
        self.db.add(payment)
        await self.db.flush()

        # Si provider physique (vendor) : pas d'appel externe, le vendeur encaisse cash
        if provider_enum == PaymentProvider.PHYSICAL_TICKET:
            payment.provider_ref = f"VENDOR-{payment.id.hex[:12].upper()}"
            await self.db.flush()
            return PaymentInitiationResult(
                payment_id=payment.id,
                provider_ref=payment.provider_ref,
                user_action_text="Encaissement en main propre par le vendeur.",
                ussd_code=None,
                redirect_url=None,
                expires_in_seconds=0,
            )

        # Sinon : appel provider externe
        provider = get_provider(provider_code)
        try:
            init = await provider.initiate(
                amount_local=amount,
                currency="KMF",
                phone=user.phone,
                reference=str(payment.id),
                metadata={"plan": plan.value, "user_id": str(user_id)},
            )
        except Exception as e:
            payment.status = PaymentStatus.FAILED
            payment.notes = f"Échec initiation: {str(e)[:200]}"
            await self.db.flush()
            raise

        payment.provider_ref = init.provider_ref
        await self.db.flush()

        logger.info(
            "payment.initiated",
            payment_id=str(payment.id),
            provider=provider_code,
            amount=amount,
        )
        return PaymentInitiationResult(
            payment_id=payment.id,
            provider_ref=init.provider_ref,
            user_action_text=init.user_action_text,
            ussd_code=init.ussd_code,
            redirect_url=init.redirect_url,
            expires_in_seconds=init.expires_in_seconds,
        )

    async def handle_webhook(
        self,
        provider_code: str,
        payload: dict,
        signature: str | None,
    ) -> Payment | None:
        """Webhook callback → marque Payment SUCCESS + active Subscription + crée OTP ticket."""
        provider = get_provider(provider_code)
        verification = await provider.verify_callback(payload, signature)
        if not verification.is_valid or not verification.provider_ref:
            logger.warning("payment.webhook_invalid", provider=provider_code)
            return None

        # Récupérer Payment par provider_ref
        result = await self.db.execute(
            select(Payment).where(Payment.provider_ref == verification.provider_ref)
        )
        payment = result.scalar_one_or_none()
        if payment is None:
            logger.warning(
                "payment.webhook_unknown_ref", ref=verification.provider_ref
            )
            return None

        if verification.status != "success":
            payment.status = PaymentStatus.FAILED
            await self.db.flush()
            return payment

        # ─── Succès → activer subscription + OTP ticket ───
        await self._on_payment_success(payment)
        return payment

    async def _on_payment_success(self, payment: Payment) -> None:
        """Création atomique : Subscription + OtpChallenge VENDOR_TICKET + grant Firestore."""
        if payment.status == PaymentStatus.SUCCESS:
            logger.info("payment.already_success", payment_id=str(payment.id))
            return

        # Extraire le plan depuis notes
        plan = self._extract_plan(payment.notes)
        scans = PLAN_SCANS.get(plan, 0)
        duration_days = PLAN_DURATION_DAYS.get(plan, 1)
        now = datetime.now(UTC)
        expires_at = now + timedelta(days=duration_days)

        # Marquer Payment SUCCESS
        payment.status = PaymentStatus.SUCCESS
        payment.completed_at = now

        # Créer Subscription
        sub = Subscription(
            tenant_id=payment.tenant_id,
            user_id=payment.user_id,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            scans_remaining=scans,
            scans_granted_total=scans,
            expires_at=expires_at,
            origin_payment_id=payment.id,
        )
        self.db.add(sub)
        await self.db.flush()

        # Créer OTP ticket vendeur (6 chiffres imprimés sur le ticket)
        otp_code = generate_otp()
        otp = OtpChallenge(
            tenant_id=payment.tenant_id,
            user_id=payment.user_id,
            phone=(await self.db.get(User, payment.user_id)).phone,
            code_hash=hash_otp(otp_code),
            otp_type=OtpType.VENDOR_TICKET,
            status=OtpStatus.PENDING,
            subscription_id=sub.id,
            recharge_ticket_code=f"NSMA-{secrets.token_hex(6).upper()[:12]}",
            expires_at=expires_at,
            max_attempts=10,
        )
        self.db.add(otp)
        await self.db.flush()

        # Mettre à jour user state + last_valid_otp
        user = await self.db.get(User, payment.user_id)
        if user:
            user.account_state = AccountState.ACTIVE
            user.credit_expires_at = expires_at
            user.last_valid_otp_hash = otp.code_hash
            user.last_valid_otp_expires_at = expires_at
            user.state_changed_at = now

        # Grant Firestore quota
        try:
            quota_svc = QuotaService()
            await quota_svc.grant_credits(
                user_id=payment.user_id,
                plan=plan.value,
                scans=scans,
                duration_days=duration_days,
            )
        except Exception as e:
            logger.warning("firestore.grant_failed_dev", error=str(e))

        await self.db.flush()
        logger.info(
            "payment.success_activated",
            payment_id=str(payment.id),
            plan=plan.value,
            scans=scans,
            otp_id=str(otp.id),
        )

    def _extract_plan(self, notes: str | None) -> SubscriptionPlan:
        """Stub : parse notes pour retrouver le plan."""
        if not notes:
            return SubscriptionPlan.DAILY
        for plan in SubscriptionPlan:
            if f"Plan: {plan.value}" in notes:
                return plan
        return SubscriptionPlan.DAILY
