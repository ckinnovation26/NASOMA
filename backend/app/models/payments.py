"""Modèle Payment — transactions Mobile Money / tickets / portail diaspora."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Enum

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.subscriptions import Subscription
    from app.models.users import User


class PaymentProvider(str, enum.Enum):
    HOLLO = "hollo"                  # Comores Telecom — prioritaire MVP
    MVOLA = "mvola"                  # Telma Madagascar/Comores
    MPESA = "mpesa"                  # Kenya
    ORANGE_MONEY = "orange_money"
    AIRTEL_MONEY = "airtel_money"
    STRIPE = "stripe"                # diaspora carte bancaire
    PHYSICAL_TICKET = "physical_ticket"  # ticket vendu en kiosque
    SCHOOL_B2B = "school_b2b"        # facturation école


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELED = "canceled"


class Payment(Base):
    __tablename__ = "payments"

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

    amount_local: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="KMF")
    amount_usd: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    provider: Mapped[PaymentProvider] = mapped_column(Enum(PaymentProvider), nullable=False)
    provider_ref: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False,
        index=True,
    )

    # Métadonnées d'origine
    vendor_id: Mapped[str | None] = mapped_column(String(40), nullable=True)            # vendeur kiosque
    school_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="payments")
    subscription: Mapped[Subscription | None] = relationship(
        back_populates="origin_payment",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<Payment {self.id} {self.amount_local} {self.currency} via {self.provider} status={self.status}>"
