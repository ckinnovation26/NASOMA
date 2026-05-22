"""Service Vendor — sélection vendeur (ticket vendor d'abord, sinon GPS proximité)."""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payments import Payment, PaymentStatus
from app.models.vendors import Vendor, VendorStatus

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class VendorRecommendation:
    """Recommandation vendeur pour assistance."""

    vendor_id: uuid.UUID
    code: str
    name: str
    contact_phone: str
    distance_km: float | None
    source: str               # 'ticket_vendor' | 'nearest_gps' | 'fallback_any'
    is_trained_level1: bool


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance en km entre deux points GPS (formule de Haversine)."""
    r = 6371.0
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


class VendorService:
    """Résolution + recommandation vendeurs pour l'assistance."""

    MAX_REASONABLE_DISTANCE_KM = 30.0     # au-delà, on cherche un plus proche

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_ticket_vendor(self, user_id: uuid.UUID) -> Vendor | None:
        """Récupère le vendeur du dernier paiement réussi du user.

        C'est le **premier choix** pour l'assistance (cf. décision 2026-05-20).
        """
        stmt = (
            select(Payment.vendor_id)
            .where(
                Payment.user_id == user_id,
                Payment.status == PaymentStatus.SUCCESS,
                Payment.vendor_id.isnot(None),
            )
            .order_by(Payment.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        vendor_code = result.scalar_one_or_none()
        if not vendor_code:
            return None

        result = await self.db.execute(
            select(Vendor).where(
                Vendor.code == vendor_code,
                Vendor.status == VendorStatus.ACTIVE,
            )
        )
        return result.scalar_one_or_none()

    async def get_nearest_vendor(
        self,
        latitude: float,
        longitude: float,
        max_distance_km: float | None = None,
        exclude_vendor_id: uuid.UUID | None = None,
    ) -> tuple[Vendor, float] | None:
        """Trouve le vendeur ACTIVE le plus proche par distance Haversine.

        Returns:
            (vendor, distance_km) ou None si aucun vendeur dans le rayon.
        """
        stmt = select(Vendor).where(
            Vendor.status == VendorStatus.ACTIVE,
            Vendor.can_provide_assistance.is_(True),
            Vendor.latitude.isnot(None),
            Vendor.longitude.isnot(None),
        )
        if exclude_vendor_id:
            stmt = stmt.where(Vendor.id != exclude_vendor_id)

        result = await self.db.execute(stmt)
        candidates = result.scalars().all()
        if not candidates:
            return None

        best: tuple[Vendor, float] | None = None
        for vendor in candidates:
            distance = haversine_km(
                latitude, longitude, vendor.latitude, vendor.longitude
            )
            if max_distance_km is not None and distance > max_distance_km:
                continue
            if best is None or distance < best[1]:
                best = (vendor, distance)

        return best

    async def recommend_for_assistance(
        self,
        user_id: uuid.UUID,
        user_latitude: float | None = None,
        user_longitude: float | None = None,
        prefer_nearest_threshold_km: float = 10.0,
    ) -> VendorRecommendation | None:
        """Recommandation vendeur selon la règle métier :

        1. Toujours essayer le vendeur du ticket en premier
        2. Si le vendeur du ticket est > prefer_nearest_threshold_km du user
           ET qu'un vendeur plus proche existe → recommander le plus proche
        3. Si pas de vendeur ticket → recommander le plus proche par GPS
        4. Si pas de GPS user → ticket vendor uniquement (ou None)
        """
        ticket_vendor = await self.get_ticket_vendor(user_id)

        # Cas 1 : pas de GPS user → on retourne le ticket vendor (ou None)
        if user_latitude is None or user_longitude is None:
            if ticket_vendor:
                return VendorRecommendation(
                    vendor_id=ticket_vendor.id,
                    code=ticket_vendor.code,
                    name=ticket_vendor.name,
                    contact_phone=ticket_vendor.contact_phone,
                    distance_km=None,
                    source="ticket_vendor",
                    is_trained_level1=ticket_vendor.is_trained_level1,
                )
            return None

        # Cas 2 : on a le GPS du user — calculer la distance au ticket vendor
        ticket_distance: float | None = None
        if (
            ticket_vendor
            and ticket_vendor.latitude is not None
            and ticket_vendor.longitude is not None
        ):
            ticket_distance = haversine_km(
                user_latitude,
                user_longitude,
                ticket_vendor.latitude,
                ticket_vendor.longitude,
            )

        # Cas 3 : ticket vendor existe ET proche → on le recommande
        if ticket_vendor and (
            ticket_distance is None or ticket_distance <= prefer_nearest_threshold_km
        ):
            return VendorRecommendation(
                vendor_id=ticket_vendor.id,
                code=ticket_vendor.code,
                name=ticket_vendor.name,
                contact_phone=ticket_vendor.contact_phone,
                distance_km=ticket_distance,
                source="ticket_vendor",
                is_trained_level1=ticket_vendor.is_trained_level1,
            )

        # Cas 4 : ticket vendor trop loin → chercher plus proche par GPS
        nearest = await self.get_nearest_vendor(
            latitude=user_latitude,
            longitude=user_longitude,
            max_distance_km=self.MAX_REASONABLE_DISTANCE_KM,
            exclude_vendor_id=ticket_vendor.id if ticket_vendor else None,
        )

        if nearest:
            vendor, distance = nearest
            # On préfère le plus proche s'il est notablement plus proche que le ticket
            if ticket_distance is None or distance < ticket_distance * 0.6:
                logger.info(
                    "vendor.recommendation_nearest_chosen",
                    user=str(user_id),
                    ticket_distance_km=ticket_distance,
                    nearest_distance_km=distance,
                )
                return VendorRecommendation(
                    vendor_id=vendor.id,
                    code=vendor.code,
                    name=vendor.name,
                    contact_phone=vendor.contact_phone,
                    distance_km=distance,
                    source="nearest_gps",
                    is_trained_level1=vendor.is_trained_level1,
                )

        # Cas 5 : on retourne le ticket vendor même s'il est loin
        if ticket_vendor:
            return VendorRecommendation(
                vendor_id=ticket_vendor.id,
                code=ticket_vendor.code,
                name=ticket_vendor.name,
                contact_phone=ticket_vendor.contact_phone,
                distance_km=ticket_distance,
                source="ticket_vendor",
                is_trained_level1=ticket_vendor.is_trained_level1,
            )

        return None
