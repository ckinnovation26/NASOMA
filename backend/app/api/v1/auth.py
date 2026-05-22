"""Endpoints d'authentification — signup SMS, verify, login (ticket vendeur), me.

Cf. docs/api.md + docs/strategie_Nasoma.md § 3 quater.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.security import create_access_token, create_refresh_token, hash_otp
from app.db.session import get_db
from app.models.otp_challenges import OtpType
from app.models.subscriptions import (
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
)
from app.models.tenants import Tenant
from app.models.users import AccountState, SignupMethod, User, UserRole
from app.schemas.auth import (
    AccountStateResponse,
    CreditStatusResponse,
    LoginRequest,
    SignupSmsRequest,
    SignupSmsResponse,
    SignupVerifyResponse,
    TokenResponse,
    UserPublic,
    VerifyOtpRequest,
)
from app.services.account_state_service import AccountStateService
from app.services.otp_service import (
    OtpExpiredError,
    OtpInvalidError,
    OtpMaxAttemptsError,
    OtpService,
)
from app.services.quota_service import QuotaService
from app.services.sms_service import SmsService

logger = structlog.get_logger(__name__)

router = APIRouter()


# ──────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────
async def _default_tenant(db: AsyncSession) -> Tenant:
    """Récupère le tenant 'KM' (seul tenant MVP)."""
    result = await db.execute(select(Tenant).where(Tenant.code == "KM"))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Tenant KM introuvable. Vérifiez la migration initiale.",
        )
    return tenant


def _build_token_response(user: User) -> TokenResponse:
    claims = {
        "tenant_id": str(user.tenant_id),
        "role": user.role.value if isinstance(user.role, UserRole) else user.role,
        "state": user.account_state.value
        if isinstance(user.account_state, AccountState)
        else user.account_state,
    }
    return TokenResponse(
        access_token=create_access_token(str(user.id), extra_claims=claims),
        refresh_token=create_refresh_token(str(user.id)),
        expires_in=settings.jwt_access_token_ttl_minutes * 60,
    )


# ──────────────────────────────────────────────
#  POST /auth/signup/sms
# ──────────────────────────────────────────────
@router.post(
    "/signup/sms",
    response_model=SignupSmsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Envoyer un OTP SMS pour la 1ère inscription",
)
async def signup_sms(
    payload: SignupSmsRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> SignupSmsResponse:
    """Génère un OTP SMS pour la 1ère inscription d'un numéro non encore vérifié.

    ⚠️ SMS = SEULE utilisation autorisée. Tous renouvellements suivants = ticket vendeur.
    """
    tenant = await _default_tenant(db)

    # Vérifier que le numéro n'est pas déjà inscrit avec phone vérifié
    existing = await db.execute(
        select(User).where(
            User.phone == payload.phone,
            User.first_signup_phone_verified.is_(True),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Ce numéro est déjà inscrit. Utilisez un ticket vendeur pour vous reconnecter.",
        )

    otp_svc = OtpService(db)
    challenge, code = await otp_svc.create_sms_first_signup(
        tenant_id=tenant.id,
        phone=payload.phone,
        ip_address=request.client.host if request.client else None,
        device_id=payload.device_id,
    )

    sms_svc = SmsService()
    delivery = await sms_svc.send_otp_sms(phone=payload.phone, otp_code=code)
    if not delivery.is_sent:
        logger.error(
            "auth.signup.sms_delivery_failed",
            phone_suffix=payload.phone[-4:],
            error=delivery.error_message,
        )
        # On ne bloque pas l'inscription si l'envoi échoue en dev/sandbox.
        # En prod, l'erreur est remontée pour retry côté client.
        if settings.app_env == "prod":
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "Envoi du SMS impossible. Réessayez dans quelques secondes.",
            )

    await db.commit()
    return SignupSmsResponse(
        challenge_id=challenge.id,
        phone=payload.phone,
        expires_in_seconds=settings.jwt_otp_ttl_minutes * 60,
    )


# ──────────────────────────────────────────────
#  POST /auth/signup/verify
# ──────────────────────────────────────────────
@router.post(
    "/signup/verify",
    response_model=SignupVerifyResponse,
    summary="Vérifier l'OTP SMS et créer le compte avec 3 scans / 7 jours",
)
async def signup_verify(
    payload: VerifyOtpRequest,
    db: AsyncSession = Depends(get_db),
) -> SignupVerifyResponse:
    """Vérifie l'OTP SMS et crée le compte avec accès Découverte (3 scans / 7 jours)."""
    tenant = await _default_tenant(db)
    otp_svc = OtpService(db)

    try:
        challenge = await otp_svc.verify_and_consume(
            phone=payload.phone,
            code=payload.code,
            otp_type=OtpType.SMS_FIRST_SIGNUP,
        )
    except OtpMaxAttemptsError as e:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, str(e)) from e
    except OtpExpiredError as e:
        raise HTTPException(status.HTTP_410_GONE, str(e)) from e
    except OtpInvalidError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e)) from e

    # Créer le user
    now = datetime.now(UTC)
    expires_at = now + timedelta(days=settings.quota_free_trial_ttl_days)

    user = User(
        tenant_id=tenant.id,
        phone=payload.phone,
        role=UserRole.STUDENT,                                 # par défaut, à raffiner Sprint 2
        locale="fr-KM",
        account_state=AccountState.ACTIVE,
        credit_expires_at=expires_at,
        last_valid_otp_hash=challenge.code_hash,
        last_valid_otp_expires_at=expires_at,
        state_changed_at=now,
        first_signup_phone_verified=True,
        first_signup_method=SignupMethod.SMS_FIREBASE,
    )
    db.add(user)
    await db.flush()

    # Lier l'OTP au user maintenant créé
    challenge.user_id = user.id

    # Créer la subscription Découverte
    sub = Subscription(
        tenant_id=tenant.id,
        user_id=user.id,
        plan=SubscriptionPlan.DISCOVERY,
        status=SubscriptionStatus.ACTIVE,
        scans_remaining=settings.quota_free_trial_scans,
        scans_granted_total=settings.quota_free_trial_scans,
        expires_at=expires_at,
        auto_renew=False,
    )
    db.add(sub)

    # Grant Firestore
    try:
        quota_svc = QuotaService()
        await quota_svc.grant_credits(
            user_id=user.id,
            plan=SubscriptionPlan.DISCOVERY.value,
            scans=settings.quota_free_trial_scans,
            duration_days=settings.quota_free_trial_ttl_days,
        )
    except Exception as e:
        # En dev sans Firestore emulator, on tolère mais on log
        logger.warning("firestore.grant_failed_dev_only", error=str(e))

    await db.commit()

    logger.info(
        "auth.signup.completed",
        user_id=str(user.id),
        phone_suffix=payload.phone[-4:],
        free_trial_scans=settings.quota_free_trial_scans,
    )

    return SignupVerifyResponse(
        user=UserPublic.model_validate(user, from_attributes=True),
        token=_build_token_response(user),
        free_trial_scans=settings.quota_free_trial_scans,
        free_trial_expires_at=expires_at,
    )


# ──────────────────────────────────────────────
#  POST /auth/login
# ──────────────────────────────────────────────
@router.post(
    "/login",
    summary="Login phone + OTP (ticket vendeur ou dernier OTP en grace)",
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Login unifié — accepte un OTP ticket vendeur OU le dernier OTP valide en grace.

    Réponse selon state :
    - ACTIVE : 200 + token + credit
    - GRACE  : 200 + token "readonly" + paywall flag
    - FROZEN : 403 + data_export_url
    """
    # Récupérer le user
    result = await db.execute(select(User).where(User.phone == payload.phone))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Ce numéro n'est pas inscrit. Inscrivez-vous d'abord via /auth/signup/sms.",
        )

    # Recalculer state en live (au cas où le cron n'est pas passé)
    state_svc = AccountStateService(db)
    info = await state_svc.get_info(user.id)
    await db.commit()                                          # persiste éventuelle transition

    # ARCHIVED → 410 Gone
    if info.state == AccountState.ARCHIVED:
        raise HTTPException(
            status.HTTP_410_GONE,
            "Compte archivé. Contactez le support pour une réactivation.",
        )

    # FROZEN → 403 + export URL
    if info.state == AccountState.FROZEN:
        return {
            "state": "frozen",
            "error": "account_frozen",
            "message": "Ton compte est suspendu. Achète un ticket chez un vendeur pour réactiver.",
            "data_export_url": f"mailto:dpo@nasoma.app?subject=Export%20donnees%20{payload.phone}",
        }

    # Vérifier le code (OTP courant OU last_valid_otp en grace)
    otp_svc = OtpService(db)
    try:
        # 1. essayer un OTP pending (ticket vendeur ou recovery)
        await otp_svc.verify_and_consume(phone=payload.phone, code=payload.code)
    except OtpInvalidError:
        # 2. fallback : vérifier le last_valid_otp_hash si en grace
        if (
            info.state == AccountState.GRACE
            and user.last_valid_otp_hash
            and user.last_valid_otp_expires_at
        ):
            if hash_otp(payload.code) == user.last_valid_otp_hash:
                logger.info("auth.login.grace_otp_used", user_id=str(user.id))
            else:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, "Code incorrect."
                ) from None
        else:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Code incorrect ou expiré."
            ) from None
    except OtpExpiredError as e:
        raise HTTPException(status.HTTP_410_GONE, str(e)) from e
    except OtpMaxAttemptsError as e:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, str(e)) from e

    # Mettre à jour last_active_at
    user.last_active_at = datetime.now(UTC)
    await db.commit()

    # Construire la réponse selon state
    if info.state == AccountState.ACTIVE:
        quota_svc = QuotaService()
        try:
            quota = await quota_svc.check(user.id)
            credit_payload = {
                "remaining_scans": quota.remaining_scans,
                "plan": quota.plan,
                "expires_at": quota.expires_at.isoformat() if quota.expires_at else None,
            }
        except Exception:
            credit_payload = {"remaining_scans": 0, "plan": "unknown"}

        return {
            "state": "active",
            "user": UserPublic.model_validate(user, from_attributes=True).model_dump(mode="json"),
            "token": _build_token_response(user).model_dump(),
            "credit": credit_payload,
        }

    # GRACE
    return {
        "state": "grace",
        "user": UserPublic.model_validate(user, from_attributes=True).model_dump(mode="json"),
        "token": _build_token_response(user).model_dump(),
        "days_remaining_grace": info.days_remaining_grace,
        "credit_expired_at": info.credit_expires_at.isoformat()
        if info.credit_expires_at
        else None,
        "message": "Lecture seule. Renouvelle pour reprendre les scans.",
        "paywall": True,
    }


# ──────────────────────────────────────────────
#  GET /me/account-state
# ──────────────────────────────────────────────
@router.get(
    "/me/account-state",
    response_model=AccountStateResponse,
    summary="État actuel du compte (calculé en live)",
)
async def get_account_state(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AccountStateResponse:
    svc = AccountStateService(db)
    info = await svc.get_info(current_user.id)
    await db.commit()
    return AccountStateResponse(
        state=info.state,
        credit_expires_at=info.credit_expires_at,
        days_remaining_grace=info.days_remaining_grace,
        days_until_freeze=info.days_until_freeze,
        can_perform_new_actions=info.can_perform_new_actions,
        paywall_required=info.paywall_required,
    )


# ──────────────────────────────────────────────
#  GET /me/credit-status
# ──────────────────────────────────────────────
@router.get(
    "/me/credit-status",
    response_model=CreditStatusResponse,
    summary="Solde de scans + expiration",
)
async def get_credit_status(
    current_user: User = Depends(get_current_user),
) -> CreditStatusResponse:
    quota_svc = QuotaService()
    status_info = await quota_svc.check(current_user.id)
    return CreditStatusResponse(
        remaining_scans=status_info.remaining_scans,
        plan=status_info.plan,
        expires_at=status_info.expires_at,
        days_until_expiry=status_info.days_until_expiry,
        is_active=status_info.is_active,
    )
