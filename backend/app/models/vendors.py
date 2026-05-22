"""Modèle Vendor — vendeurs de tickets de recharge (kiosque, école, diaspora).

Géolocalisation pour recommander le vendeur le plus proche en cas d'assistance.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime, Enum

from app.db.session import Base


class VendorType(str, enum.Enum):
    KIOSQUE = "kiosque"               # vendeur indépendant (kiosque, boutique)
    SCHOOL = "school"                 # école qui vend des tickets à ses familles
    DIASPORA_PORTAL = "diaspora_portal"   # portail web utilisé par diaspora
    AGENT = "agent"                   # agent commercial Nasoma


class VendorStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Vendor(Base):
    """Un vendeur enregistré dans le réseau de distribution Nasoma."""

    __tablename__ = "vendors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    vendor_type: Mapped[VendorType] = mapped_column(Enum(VendorType), nullable=False)
    status: Mapped[VendorStatus] = mapped_column(
        Enum(VendorStatus),
        default=VendorStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(120), nullable=True)

    # Géolocalisation — pour recommandation par proximité
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    address_line: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    island: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # Pour Comores : Ngazidja, Anjouan, Mohéli

    # Capacités assistance
    can_provide_assistance: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_trained_level1: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    trained_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    # Commercial
    commission_percent: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    last_active_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<Vendor {self.code} {self.vendor_type} {self.city}>"
