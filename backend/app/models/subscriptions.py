"""Modèle Subscription — abonnement actif d'un utilisateur."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Enum

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.payments import Payment
    from app.models.users import User


class SubscriptionPlan(str, enum.Enum):
    """Plans Nasoma — verrouillés business (cf. docs/pricing.md)."""

    DISCOVERY = "discovery"          # 3 scans / 7 jours, gratuit (1ère inscription)
    DAILY = "daily"                  # 100 KMF · 5 scans / 24h
    THREE_DAY = "three_day"          # 250 KMF · 15 scans / 3 jours (préparation examen)
    WEEKLY = "weekly"                # 500 KMF · 30 scans / 7 jours
    MONTHLY_PER_CHILD = "monthly"    # 1 500 KMF/enfant · 120 scans / 30 jours
    SCHOOL_B2B = "school_b2b"        # négocié


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    GRACE = "grace"             # crédit expiré, lecture seule 30j
    EXPIRED = "expired"         # > 30j de grace
    CANCELED = "canceled"       # annulé par user/admin


class Subscription(Base):
    __tablename__ = "subscriptions"

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
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    plan: Mapped[SubscriptionPlan] = mapped_column(Enum(SubscriptionPlan), nullable=False)
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus),
        default=SubscriptionStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    # Quota et expiration
    scans_remaining: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    scans_granted_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False)

    # Lien au paiement origine (null pour Découverte gratuit)
    origin_payment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payments.id"),
        nullable=True,
    )

    canceled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_reason: Mapped[str | None] = mapped_column(String(120), nullable=True)

    user: Mapped[User] = relationship(back_populates="subscriptions")
    origin_payment: Mapped[Payment | None] = relationship(
        foreign_keys=[origin_payment_id],
        back_populates="subscription",
    )

    def __repr__(self) -> str:
        return f"<Subscription {self.id} {self.plan} status={self.status} scans={self.scans_remaining}>"
