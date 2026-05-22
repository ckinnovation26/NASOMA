"""Endpoints billing post-paid + vendor dashboard + diaspora GPS."""

from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import generate_otp, hash_otp
from app.db.session import get_db
from app.models.billing import VideoAssistanceStatus
from app.models.tenants import Tenant
from app.models.users import User
from app.models.vendors import Vendor, VendorStatus
from app.schemas.billing import (
    DiasporaPurchaseRequest,
    DiasporaPurchaseResponse,
    FreeAlternativeVendor,
    OutstandingBillPublic,
    VendorCustomerDashboardResponse,
    VendorNearbyRecommendation,
    VendorRechargePayload,
    VendorRechargeResponse,
    VideoAssistanceConfirmPayload,
    VideoAssistanceDisclosureResponse,
    VideoAssistanceEndedResponse,
    VideoAssistanceRequestPayload,
    VideoAssistanceStartedResponse,
)
from app.services.billing_service import (
    AccountNotActiveError,
    BillingError,
    BillingService,
)
from app.services.vendor_service import VendorService, haversine_km

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


# ════════════════════════════════════════════════════════════════
#  Video assistance (ACTIVE only, post-paid 200 KMF/10 min)
# ════════════════════════════════════════════════════════════════
@router.post(
    "/support/video-assistance/request",
    response_model=VideoAssistanceDisclosureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Demander assistance vidéo — retourne le disclosure tarifaire",
)
async def request_video_assistance(
    payload: VideoAssistanceRequestPayload,
    db: AsyncSession = Depends(get_db),
) -> VideoAssistanceDisclosureResponse:
    """ÉTAPE 1 — Le user demande l'assistance.

    Backend vérifie ACTIVE → retourne disclosure_text à présenter.
    Le user doit ensuite POST /confirm avec user_consent=true.
    """
    tenant_id = await _default_tenant_id(db)
    svc = BillingService(db)
    try:
        session = await svc.request_video_assistance(payload.student_id, tenant_id)
    except AccountNotActiveError as e:
        await db.commit()
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, str(e)) from e
    except BillingError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e

    # Récupérer le vendeur habituel pour proposer l'alternative GRATUITE en premier
    vendor_svc = VendorService(db)
    usual_vendor = await vendor_svc.get_ticket_vendor(payload.student_id)
    free_alt = None
    if usual_vendor:
        free_alt = FreeAlternativeVendor(
            vendor_id=usual_vendor.id,
            code=usual_vendor.code,
            name=usual_vendor.name,
            contact_phone=usual_vendor.contact_phone,
            distance_km=None,
            city=usual_vendor.city,
            relationship="usual_vendor",
            is_trained_level1=usual_vendor.is_trained_level1,
        )

    await db.commit()
    return VideoAssistanceDisclosureResponse(
        session_id=session.id,
        free_alternative_text=settings.video_assistance_free_alternative_text,
        free_alternative_vendor=free_alt,
        rate_kmf_per_10min=session.rate_kmf_per_10min,
        max_session_minutes=settings.video_assistance_max_session_minutes,
        disclosure_text=settings.video_assistance_disclosure_text,
    )


@router.post(
    "/support/video-assistance/{session_id}/confirm",
    summary="Confirmer la tarification — disclosure acceptée",
)
async def confirm_video_disclosure(
    session_id: uuid.UUID,
    payload: VideoAssistanceConfirmPayload,
    student_id: uuid.UUID,                       # TODO Sprint 2.5 : depuis JWT
    db: AsyncSession = Depends(get_db),
) -> dict:
    svc = BillingService(db)
    try:
        session = await svc.confirm_disclosure(session_id, student_id)
    except BillingError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e
    await db.commit()
    return {
        "session_id": str(session.id),
        "status": session.status.value if hasattr(session.status, "value") else str(session.status),
        "consent_recorded_at": session.disclosed_at.isoformat() if session.disclosed_at else None,
        "next_step": "Attendez qu'un agent rejoigne la session.",
    }


@router.post(
    "/internal/video-assistance/{session_id}/start",
    response_model=VideoAssistanceStartedResponse,
    summary="[INTERNAL] L'agent démarre la session vidéo",
)
async def start_video_session(
    session_id: uuid.UUID,
    agent_id: uuid.UUID,
    agent_name: str,
    video_room_url: str,
    db: AsyncSession = Depends(get_db),
) -> VideoAssistanceStartedResponse:
    """Endpoint interne — appelé par le système d'agents quand un agent prend la session."""
    svc = BillingService(db)
    try:
        session = await svc.start_session(
            session_id=session_id,
            agent_id=agent_id,
            agent_name=agent_name,
            video_room_url=video_room_url,
        )
    except BillingError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e
    await db.commit()
    return VideoAssistanceStartedResponse(
        session_id=session.id,
        video_room_url=session.video_room_url or "",
        agent_name=session.agent_name or "",
        started_at=session.started_at,
    )


@router.post(
    "/support/video-assistance/{session_id}/end",
    response_model=VideoAssistanceEndedResponse,
    summary="Terminer la session — calcule durée + crée facture en attente",
)
async def end_video_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> VideoAssistanceEndedResponse:
    svc = BillingService(db)
    try:
        session, bill = await svc.end_session_and_bill(session_id)
    except BillingError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e
    await db.commit()

    return VideoAssistanceEndedResponse(
        session_id=session.id,
        duration_seconds=session.duration_seconds or 0,
        billed_minutes=session.billed_minutes_rounded_up or 0,
        billed_amount_kmf=session.billed_amount_kmf or 0,
        outstanding_bill_id=bill.id,
        message=(
            f"Session terminée. {session.billed_amount_kmf} KMF seront "
            f"prélevés à votre prochaine recharge chez votre vendeur."
        ),
    )


# ════════════════════════════════════════════════════════════════
#  Vendor dashboard — visible AVANT toute transaction
# ════════════════════════════════════════════════════════════════
@router.get(
    "/vendor/customers/{phone}/dashboard",
    response_model=VendorCustomerDashboardResponse,
    summary="Dashboard client pour vendeur — factures + état compte",
)
async def get_vendor_customer_dashboard(
    phone: str,
    db: AsyncSession = Depends(get_db),
) -> VendorCustomerDashboardResponse:
    """Affiché au vendeur dès qu'il tape le numéro du client.

    ⚠️ Le vendeur DOIT présenter ces infos au client AVANT toute transaction.
    """
    svc = BillingService(db)
    dashboard = await svc.get_customer_dashboard(phone)
    if dashboard is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Client non trouvé.")

    return VendorCustomerDashboardResponse(
        user_id=dashboard.user_id,
        phone=dashboard.phone,
        full_name=dashboard.full_name,
        account_state=dashboard.account_state,  # type: ignore[arg-type]
        outstanding_bills=[
            OutstandingBillPublic(
                bill_id=b.id,
                kind=b.kind.value if hasattr(b.kind, "value") else str(b.kind),
                description=b.description,
                amount_kmf=b.amount_kmf,
                created_at=b.created_at,
                grace_until=b.grace_until,
            )
            for b in dashboard.outstanding_bills
        ],
        total_due_kmf=dashboard.total_due_kmf,
        eligible_for_video_assistance=dashboard.eligible_for_video_assistance,
        available_plans=["daily", "three_day", "weekly", "monthly"],
    )


@router.post(
    "/vendor/recharge",
    response_model=VendorRechargeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Vendor enregistre transaction — règle dettes + recharge",
)
async def vendor_recharge(
    payload: VendorRechargePayload,
    db: AsyncSession = Depends(get_db),
) -> VendorRechargeResponse:
    """Le vendeur enregistre la transaction après accord client.

    Le client a choisi explicitement :
    - Régler des factures (settle_bill_ids non vide)
    - Recharger un plan (new_plan défini)
    - Les deux

    TODO Sprint 2.5 : créer Payment + Subscription + OtpChallenge complets.
    Pour Sprint 2 — on règle les factures + retourne reçu.
    """
    # Lookup client
    result = await db.execute(select(User).where(User.phone == payload.phone))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Client non trouvé.")

    # TODO Sprint 2.5 : créer Payment réel + Subscription
    # Pour Sprint 2 : règlement factures uniquement + OTP placeholder
    fake_payment_id = uuid.uuid4()
    svc = BillingService(db)
    settled_count = 0
    if payload.settle_bill_ids:
        settled_count = await svc.settle_bills(
            bill_ids=payload.settle_bill_ids,
            payment_id=fake_payment_id,
            vendor_id=payload.vendor_code,
        )

    settled_total = sum(
        b.amount_kmf
        for b in (
            await db.execute(
                select(__import__("app.models.billing", fromlist=["OutstandingBill"]).OutstandingBill).where(
                    __import__(
                        "app.models.billing", fromlist=["OutstandingBill"]
                    ).OutstandingBill.id.in_(payload.settle_bill_ids)
                )
            )
        ).scalars().all()
    )

    new_subscription_id = None
    new_otp_code = None
    if payload.new_plan:
        new_otp_code = generate_otp()
        # TODO Sprint 2.5 : créer Subscription + OtpChallenge VENDOR_TICKET
        # avec ticket physique imprimé

    await db.commit()

    receipt = (
        f"Reçu Nasoma — {payload.vendor_code}\n"
        f"Client : {payload.phone}\n"
        f"Factures réglées : {settled_count} ({settled_total} KMF)\n"
        f"Nouveau plan : {payload.new_plan or 'Aucun'}\n"
        f"Montant reçu : {payload.amount_received_kmf} KMF\n"
        + (f"Code OTP du ticket : {new_otp_code}\n" if new_otp_code else "")
        + "⚠️ GARDEZ CE TICKET — le dernier code reste votre clé d'accès\n"
        "à votre compte pendant 30 jours après expiration."
    )

    return VendorRechargeResponse(
        payment_id=fake_payment_id,
        bills_settled_count=settled_count,
        bills_settled_total_kmf=settled_total,
        new_subscription_id=new_subscription_id,
        new_otp_code=new_otp_code,
        receipt_text=receipt,
    )


# ════════════════════════════════════════════════════════════════
#  Diaspora purchase — vendeur proche de l'enfant par GPS
# ════════════════════════════════════════════════════════════════
@router.post(
    "/diaspora/purchase",
    response_model=DiasporaPurchaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Achat depuis portail diaspora — recommande vendeur proche de l'enfant",
)
async def diaspora_purchase(
    payload: DiasporaPurchaseRequest,
    db: AsyncSession = Depends(get_db),
) -> DiasporaPurchaseResponse:
    """Parent diaspora paye en ligne → on recommande des vendeurs proches de
    L'ENFANT (pas du parent diaspora) pour assistance physique éventuelle.

    Utilise les coords home_latitude/home_longitude du profil enfant.
    Fallback : recherche par home_city / home_island.
    """
    # Lookup enfant
    result = await db.execute(
        select(User).where(User.phone == payload.target_child_phone)
    )
    child = result.scalar_one_or_none()
    if child is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Profil enfant introuvable. Inscrivez-le d'abord depuis l'app.",
        )

    # TODO Sprint 2.5 : créer Payment Stripe + Subscription + OTP réel
    fake_payment_id = uuid.uuid4()
    otp_code = generate_otp()
    # Hashé pour persistance (mais ici on retourne aussi le clair au parent diaspora)

    # ─── Recommandation vendeurs proches de l'enfant ───
    nearby: list[VendorNearbyRecommendation] = []
    if child.home_latitude is not None and child.home_longitude is not None:
        # GPS direct
        vendor_svc = VendorService(db)
        result = await db.execute(
            select(Vendor).where(
                Vendor.status == VendorStatus.ACTIVE,
                Vendor.can_provide_assistance.is_(True),
                Vendor.latitude.isnot(None),
                Vendor.longitude.isnot(None),
            )
        )
        candidates = result.scalars().all()
        scored = []
        for v in candidates:
            distance = haversine_km(
                child.home_latitude, child.home_longitude, v.latitude, v.longitude
            )
            if distance <= 30.0:
                scored.append((v, distance))
        scored.sort(key=lambda x: x[1])
        for v, distance in scored[:3]:
            nearby.append(
                VendorNearbyRecommendation(
                    vendor_id=v.id,
                    code=v.code,
                    name=v.name,
                    contact_phone=v.contact_phone,
                    distance_km=distance,
                    city=v.city,
                    island=v.island,
                    is_trained_level1=v.is_trained_level1,
                )
            )
    elif child.home_city:
        # Fallback : par ville
        result = await db.execute(
            select(Vendor).where(
                Vendor.status == VendorStatus.ACTIVE,
                Vendor.city == child.home_city,
                Vendor.can_provide_assistance.is_(True),
            ).limit(3)
        )
        for v in result.scalars().all():
            nearby.append(
                VendorNearbyRecommendation(
                    vendor_id=v.id,
                    code=v.code,
                    name=v.name,
                    contact_phone=v.contact_phone,
                    distance_km=None,
                    city=v.city,
                    island=v.island,
                    is_trained_level1=v.is_trained_level1,
                )
            )

    await db.commit()

    logger.info(
        "diaspora.purchase",
        child_phone=payload.target_child_phone[-4:],
        plan=payload.plan,
        nearby_count=len(nearby),
        payer_country=payload.payer_country,
    )

    return DiasporaPurchaseResponse(
        payment_id=fake_payment_id,
        target_child_phone=payload.target_child_phone,
        plan=payload.plan,
        otp_code=otp_code,
        nearby_vendors_for_assistance=nearby,
    )
