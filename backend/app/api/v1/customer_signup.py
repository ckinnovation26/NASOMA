"""Endpoints signup customer — vendor portal + diaspora avec KYC + WhatsApp OTP."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import generate_otp, hash_otp
from app.db.session import get_db
from app.models.identity import DocumentType, IdentityDocument, KycStatus
from app.models.otp_challenges import OtpChallenge, OtpStatus, OtpType
from app.models.subscriptions import (
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
)
from app.models.tenants import Tenant
from app.models.users import AccountState, SignupMethod, User, UserRole
from app.schemas.customer_signup import (
    DiasporaSignupCustomerResponse,
    SelfSignupAcceptedResponse,
    SelfSignupPayload,
    VendorSignupCustomerResponse,
    WhatsAppGuidanceResponse,
)
from app.services.communication_service import CommunicationService
from app.services.quota_service import QuotaService
from app.services.vendor_service import VendorService

logger = structlog.get_logger(__name__)

router = APIRouter()


async def _default_tenant(db: AsyncSession) -> Tenant:
    result = await db.execute(select(Tenant).where(Tenant.code == "KM"))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Tenant KM introuvable."
        )
    return tenant


# ══════════════════════════════════════════════
#  POST /auth/signup/self
#  Self-signup depuis app — pré-check WhatsApp obligatoire
# ══════════════════════════════════════════════
@router.post(
    "/auth/signup/self",
    response_model=SelfSignupAcceptedResponse | WhatsAppGuidanceResponse,
    summary="Self-signup app — vérifie WhatsApp avant envoi OTP",
)
async def self_signup(
    payload: SelfSignupPayload,
    db: AsyncSession = Depends(get_db),
) -> SelfSignupAcceptedResponse | WhatsAppGuidanceResponse:
    """Self-signup depuis l'app mobile.

    ⚠️ PRÉ-CHECK OBLIGATOIRE :
    - Si `has_whatsapp=false` → renvoyer vers vendeur ou installation WhatsApp
    - Si `has_whatsapp=true` → créer user + envoyer OTP via WhatsApp

    Raison : éviter coût API WhatsApp à perte + garantir canal de relance.
    """
    if not payload.consent_data_processing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Consentement RGPD obligatoire.")

    # ─── Cas 1 : pas de WhatsApp → orienter vendeur ───
    if not payload.has_whatsapp:
        vendor_svc = VendorService(db)
        nearby: list[dict] = []
        if (
            payload.user_latitude is not None
            and payload.user_longitude is not None
        ):
            nearest = await vendor_svc.get_nearest_vendor(
                latitude=payload.user_latitude,
                longitude=payload.user_longitude,
                max_distance_km=30.0,
            )
            if nearest:
                vendor, distance = nearest
                nearby.append(
                    {
                        "vendor_id": str(vendor.id),
                        "code": vendor.code,
                        "name": vendor.name,
                        "contact_phone": vendor.contact_phone,
                        "distance_km": round(distance, 2),
                        "city": vendor.city,
                    }
                )

        logger.info(
            "self_signup.no_whatsapp_redirected",
            phone_suffix=payload.phone[-4:],
            nearby_count=len(nearby),
        )

        return WhatsAppGuidanceResponse(
            nearby_vendors=nearby,
        )

    # ─── Cas 2 : has_whatsapp=true → flow normal ───
    # Vérifier que le numéro n'est pas déjà inscrit
    existing = await db.execute(select(User).where(User.phone == payload.phone))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Ce numéro est déjà inscrit. Si tu as perdu l'accès, va voir un vendeur.",
        )

    tenant = await _default_tenant(db)
    now = datetime.now(UTC)
    expires_at = now + timedelta(days=settings.quota_free_trial_ttl_days)

    user = User(
        tenant_id=tenant.id,
        phone=payload.phone,
        role=UserRole.STUDENT,
        full_name=payload.full_name,
        grade_level=payload.grade_level,
        home_city=payload.home_city,
        home_island=payload.home_island,
        account_state=AccountState.ACTIVE,
        credit_expires_at=expires_at,
        state_changed_at=now,
        first_signup_phone_verified=False,             # validé une fois OTP vérifié
        first_signup_method=SignupMethod.WHATSAPP_VENDOR,  # cas self → mais flow WhatsApp
        kyc_status="not_verified",                     # self = pas de pièce → ops sensibles bloquées
        preferred_otp_channel="whatsapp",
        app_installed=True,                            # déjà installée pour self-signup
        last_app_active_at=now,
    )
    db.add(user)
    await db.flush()

    # OTP + WhatsApp
    otp_code = generate_otp()
    challenge = OtpChallenge(
        tenant_id=tenant.id,
        user_id=user.id,
        phone=payload.phone,
        code_hash=hash_otp(otp_code),
        otp_type=OtpType.SMS_FIRST_SIGNUP,
        status=OtpStatus.PENDING,
        expires_at=expires_at,
        device_id=payload.device_id,
    )
    db.add(challenge)
    user.last_valid_otp_hash = challenge.code_hash
    user.last_valid_otp_expires_at = expires_at
    await db.flush()

    # Subscription Découverte 3 scans / 7j
    sub = Subscription(
        tenant_id=tenant.id,
        user_id=user.id,
        plan=SubscriptionPlan.DISCOVERY,
        status=SubscriptionStatus.ACTIVE,
        scans_remaining=settings.quota_free_trial_scans,
        scans_granted_total=settings.quota_free_trial_scans,
        expires_at=expires_at,
    )
    db.add(sub)

    try:
        quota_svc = QuotaService()
        await quota_svc.grant_credits(
            user_id=user.id,
            plan=SubscriptionPlan.DISCOVERY.value,
            scans=settings.quota_free_trial_scans,
            duration_days=settings.quota_free_trial_ttl_days,
        )
    except Exception as e:
        logger.warning("firestore.grant_failed_dev", error=str(e))

    # Envoi WhatsApp
    comm = CommunicationService(db)
    sent = await comm.send_first_signup_otp(
        user=user,
        otp_code=otp_code,
        free_scans=settings.quota_free_trial_scans,
        ttl_days=settings.quota_free_trial_ttl_days,
    )

    await db.commit()

    logger.info(
        "self_signup.accepted",
        user_id=str(user.id),
        whatsapp_sent=sent,
    )

    return SelfSignupAcceptedResponse(
        user_id=user.id,
        phone=payload.phone,
        free_trial_scans=settings.quota_free_trial_scans,
        free_trial_expires_at=expires_at,
        whatsapp_delivery_status="sent" if sent else "failed",
        kyc_status="not_verified",
    )


# ══════════════════════════════════════════════
#  POST /vendor/customers/signup
# ══════════════════════════════════════════════
@router.post(
    "/vendor/customers/signup",
    response_model=VendorSignupCustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Vendor enregistre un nouveau client en personne (avec KYC + WhatsApp OTP)",
)
async def vendor_signup_customer(
    phone: str = Form(...),
    full_name: str = Form(...),
    grade_level: str | None = Form(None),
    home_city: str | None = Form(None),
    home_island: str | None = Form(None),
    guardian_full_name: str = Form(...),
    guardian_document_type: str = Form("cni"),
    guardian_relationship: str = Form(...),
    vendor_code: str = Form(...),
    customer_has_whatsapp: bool = Form(...),
    consent_data_processing: bool = Form(...),
    guardian_id_image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> VendorSignupCustomerResponse:
    """Flow 1ère inscription via vendeur :
    0. ⚠️ Vendeur vérifie que le client a WhatsApp installé sur son téléphone
    1. Vendeur scanne pièce d'identité + saisit phone + nom
    2. Backend crée User + IdentityDocument (status PENDING)
    3. Backend génère OTP + envoie via WhatsApp avec onboarding multimédia
    4. Backend retourne OTP au vendeur (backup si WhatsApp tarde)
    """
    if not consent_data_processing:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Consentement RGPD obligatoire.",
        )

    # ⚠️ WhatsApp obligatoire — sinon le client ne pourra pas recevoir l'OTP
    if not customer_has_whatsapp:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            (
                "Le client doit avoir WhatsApp installé pour recevoir son code OTP. "
                "Aide-le à installer WhatsApp d'abord, puis recommence l'inscription."
            ),
        )

    # Vérifier que le numéro n'est pas déjà enregistré
    existing = await db.execute(select(User).where(User.phone == phone))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Ce numéro est déjà inscrit. Le vendeur peut recharger via /vendor/recharge.",
        )

    tenant = await _default_tenant(db)
    now = datetime.now(UTC)
    expires_at = now + timedelta(days=settings.quota_free_trial_ttl_days)

    # 1. Upload pièce d'identité du PARENT/TUTEUR (TODO Sprint 3.5 : Cloud Storage chiffré)
    image_bytes = await guardian_id_image.read()
    image_storage_key = f"kyc/{phone[-8:]}/{uuid.uuid4().hex}.jpg"
    # En dev, on simule

    # 2. Créer User (l'enfant ; mais responsable légal = parent/tuteur via IdentityDocument)
    user = User(
        tenant_id=tenant.id,
        phone=phone,
        role=UserRole.STUDENT,
        full_name=full_name,
        grade_level=grade_level,
        home_city=home_city,
        home_island=home_island,
        account_state=AccountState.ACTIVE,
        credit_expires_at=expires_at,
        state_changed_at=now,
        first_signup_phone_verified=True,
        first_signup_method=SignupMethod.WHATSAPP_VENDOR,
        kyc_status="pending",
        preferred_otp_channel="whatsapp",
        app_installed=False,
    )
    db.add(user)
    await db.flush()

    # 3. Créer IdentityDocument du parent/tuteur
    try:
        doc_type_enum = DocumentType(guardian_document_type)
    except ValueError as e:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"guardian_document_type invalide: {guardian_document_type}",
        ) from e

    identity = IdentityDocument(
        tenant_id=tenant.id,
        user_id=user.id,
        document_type=doc_type_enum,
        image_storage_key=image_storage_key,
        extracted_name=guardian_full_name,
        uploaded_by_source=f"vendor_in_person:{guardian_relationship}",
        verified_by_vendor_code=vendor_code,
        verified_at=now,
        kyc_status=KycStatus.VERIFIED,                  # vendeur en personne = preuve
    )
    db.add(identity)
    user.kyc_status = "verified"
    await db.flush()

    # 4. Générer OTP + envoyer WhatsApp
    otp_code = generate_otp()
    challenge = OtpChallenge(
        tenant_id=tenant.id,
        user_id=user.id,
        phone=phone,
        code_hash=hash_otp(otp_code),
        otp_type=OtpType.SMS_FIRST_SIGNUP,              # réutilise enum existant (rename Sprint 3.5)
        status=OtpStatus.PENDING,
        expires_at=expires_at,                          # OTP = clé d'accès pendant 7j
    )
    db.add(challenge)
    user.last_valid_otp_hash = challenge.code_hash
    user.last_valid_otp_expires_at = expires_at
    await db.flush()

    # 5. Créer subscription Découverte (3 scans / 7j)
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

    # 6. Grant Firestore quota
    try:
        quota_svc = QuotaService()
        await quota_svc.grant_credits(
            user_id=user.id,
            plan=SubscriptionPlan.DISCOVERY.value,
            scans=settings.quota_free_trial_scans,
            duration_days=settings.quota_free_trial_ttl_days,
        )
    except Exception as e:
        logger.warning("firestore.grant_failed_dev", error=str(e))

    # 7. Envoyer OTP via WhatsApp (onboarding multimédia)
    comm = CommunicationService(db)
    whatsapp_sent = await comm.send_first_signup_otp(
        user=user,
        otp_code=otp_code,
        free_scans=settings.quota_free_trial_scans,
        ttl_days=settings.quota_free_trial_ttl_days,
    )
    whatsapp_status = "sent" if whatsapp_sent else "failed"

    await db.commit()

    logger.info(
        "vendor.customer_signed_up",
        user_id=str(user.id),
        vendor_code=vendor_code,
        whatsapp_status=whatsapp_status,
    )

    return VendorSignupCustomerResponse(
        user_id=user.id,
        phone=phone,
        otp_code_for_vendor_backup=otp_code,             # Le vendeur peut lire si WhatsApp tarde
        whatsapp_delivery_status=whatsapp_status,
        free_trial_scans=settings.quota_free_trial_scans,
        free_trial_expires_at=expires_at,
        identity_document_id=identity.id,
        kyc_status="verified",
        message=(
            f"Client enregistré. OTP envoyé via WhatsApp au {phone}. "
            "Vous pouvez aussi lui dicter le code. "
            f"3 scans gratuits valables {settings.quota_free_trial_ttl_days} jours."
        ),
    )


# ══════════════════════════════════════════════
#  POST /diaspora/customers/signup-and-purchase
# ══════════════════════════════════════════════
@router.post(
    "/diaspora/customers/signup-and-purchase",
    response_model=DiasporaSignupCustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Diaspora 1er achat — KYC enfant + WhatsApp OTP + recommandations vendeurs proches",
)
async def diaspora_signup_and_purchase(
    target_child_phone: str = Form(...),
    child_full_name: str = Form(...),
    child_grade_level: str | None = Form(None),
    child_home_city: str | None = Form(None),
    child_home_island: str | None = Form(None),
    guardian_full_name: str = Form(...),
    guardian_document_type: str = Form("passport"),
    guardian_relationship: str = Form(...),
    plan: str = Form(...),
    payer_email: str = Form(...),
    payer_country: str | None = Form(None),
    child_has_whatsapp: bool = Form(...),
    consent_data_processing: bool = Form(...),
    guardian_id_image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> DiasporaSignupCustomerResponse:
    """Flow 1er achat diaspora simplifié :
    0. ⚠️ Vérifier child_has_whatsapp + consent_data_processing
    1. Parent diaspora saisit infos enfant + sa propre pièce d'identité
    2. Paiement Stripe initié
    3. User créé + IdentityDocument (parent/tuteur) + WhatsApp OTP enfant
    """
    if not consent_data_processing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Consentement obligatoire.")

    # ⚠️ WhatsApp obligatoire pour l'enfant (sinon OTP non reçu malgré paiement)
    if not child_has_whatsapp:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            (
                "L'enfant doit avoir WhatsApp installé sur son téléphone au pays. "
                "Sans WhatsApp, il ne pourra pas recevoir le code OTP même après votre "
                "paiement. Vérifiez d'abord, puis recommencez."
            ),
        )

    existing = await db.execute(
        select(User).where(User.phone == target_child_phone)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Cet enfant a déjà un compte. Utilisez /diaspora/purchase pour recharger.",
        )

    tenant = await _default_tenant(db)
    now = datetime.now(UTC)
    expires_at = now + timedelta(days=settings.quota_free_trial_ttl_days)

    # 1. Lire la pièce d'identité du parent/tuteur (1 SEULE pièce)
    guardian_doc_bytes = await guardian_id_image.read()
    guardian_doc_key = (
        f"kyc/diaspora/{target_child_phone[-8:]}/guardian-{uuid.uuid4().hex}.jpg"
    )

    # 2. Créer User (l'enfant ; responsable légal = parent/tuteur via IdentityDocument)
    user = User(
        tenant_id=tenant.id,
        phone=target_child_phone,
        role=UserRole.STUDENT,
        full_name=child_full_name,
        grade_level=child_grade_level,
        home_city=child_home_city,
        home_island=child_home_island,
        account_state=AccountState.ACTIVE,
        credit_expires_at=expires_at,
        state_changed_at=now,
        first_signup_phone_verified=True,
        first_signup_method=SignupMethod.WHATSAPP_DIASPORA,
        kyc_status="pending",                            # vérifié à la review admin
        preferred_otp_channel="whatsapp",
        app_installed=False,
    )
    db.add(user)
    await db.flush()

    # 3. Créer IdentityDocument du parent/tuteur (1 seule pièce par compte)
    try:
        guardian_doc_type = DocumentType(guardian_document_type)
    except ValueError as e:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"guardian_document_type invalide: {guardian_document_type}",
        ) from e

    child_identity = IdentityDocument(
        tenant_id=tenant.id,
        user_id=user.id,
        document_type=guardian_doc_type,
        image_storage_key=guardian_doc_key,
        extracted_name=guardian_full_name,
        uploaded_by_source=f"diaspora_portal:{guardian_relationship}",
        kyc_status=KycStatus.PENDING,                    # review admin
    )
    db.add(child_identity)
    await db.flush()

    # 4. Subscription Découverte
    sub = Subscription(
        tenant_id=tenant.id,
        user_id=user.id,
        plan=SubscriptionPlan.DISCOVERY,
        status=SubscriptionStatus.ACTIVE,
        scans_remaining=settings.quota_free_trial_scans,
        scans_granted_total=settings.quota_free_trial_scans,
        expires_at=expires_at,
    )
    db.add(sub)

    # 5. OTP WhatsApp à l'enfant
    otp_code = generate_otp()
    challenge = OtpChallenge(
        tenant_id=tenant.id,
        user_id=user.id,
        phone=target_child_phone,
        code_hash=hash_otp(otp_code),
        otp_type=OtpType.SMS_FIRST_SIGNUP,
        status=OtpStatus.PENDING,
        expires_at=expires_at,
    )
    db.add(challenge)
    user.last_valid_otp_hash = challenge.code_hash
    user.last_valid_otp_expires_at = expires_at

    try:
        quota_svc = QuotaService()
        await quota_svc.grant_credits(
            user_id=user.id,
            plan=SubscriptionPlan.DISCOVERY.value,
            scans=settings.quota_free_trial_scans,
            duration_days=settings.quota_free_trial_ttl_days,
        )
    except Exception as e:
        logger.warning("firestore.grant_failed_dev", error=str(e))

    comm = CommunicationService(db)
    whatsapp_sent = await comm.send_first_signup_otp(
        user=user,
        otp_code=otp_code,
        free_scans=settings.quota_free_trial_scans,
        ttl_days=settings.quota_free_trial_ttl_days,
    )

    # 6. TODO Sprint 3.5 : créer Payment Stripe + redirect URL
    fake_payment_id = uuid.uuid4()
    fake_redirect = "https://nasoma.app/checkout/diaspora-pending"

    await db.commit()

    logger.info(
        "diaspora.signed_up_and_purchased",
        user_id=str(user.id),
        plan=plan,
        payer_country=payer_country,
    )

    return DiasporaSignupCustomerResponse(
        user_id=user.id,
        target_child_phone=target_child_phone,
        payment_id=fake_payment_id,
        payment_redirect_url=fake_redirect,
        otp_code=otp_code,
        whatsapp_delivery_status="sent" if whatsapp_sent else "failed",
        identity_document_id=child_identity.id,
    )
