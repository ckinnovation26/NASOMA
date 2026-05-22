"""Modèle RechargeTicket — tickets physiques générés par les vendeurs.

Un ticket = un code 16 caractères format NSMA-XXXX-XXXX-XXXX signé HMAC.
Le ticket contient l'OTP qui sert de :
  1. Mot de passe d'accès (combiné au phone)
  2. Preuve du paiement effectué
  3. Activation des crédits

⚠️ Le message obligatoire sur chaque ticket est :
   "GARDEZ CE TICKET — le dernier code est votre clé d'accès au compte
    pendant 30 jours après expiration."
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Enum

from app.db.session import Base
from app.models.subscriptions import SubscriptionPlan

if TYPE_CHECKING:
    from app.models.users import User


class TicketStatus(str, enum.Enum):
    GENERATED = "generated"      # créé par le vendeur, non encore activé
    REDEEMED = "redeemed"        # activé par le client dans l'app
    EXPIRED = "expired"          # non activé dans le délai
    CANCELED = "canceled"        # annulé par le vendeur (erreur de saisie)


class RechargeTicket(Base):
    __tablename__ = "recharge_tickets"

    # Code public 16 chars NSMA-XXXX-XXXX-XXXX
    code: Mapped[str] = mapped_column(String(20), primary_key=True)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )
    # HMAC signature pour vérifier l'authenticité du code
    code_hmac: Mapped[str] = mapped_column(String(64), nullable=False)

    plan: Mapped[SubscriptionPlan] = mapped_column(Enum(SubscriptionPlan), nullable=False)
    scans_granted: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    duration_days: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # Origine
    vendor_id: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    school_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    batch_id: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    target_phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # Cycle de vie
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus),
        default=TicketStatus.GENERATED,
        nullable=False,
        index=True,
    )
    redeemed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    redeemed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    sold_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    redeemed_by: Mapped[User | None] = relationship()

    def __repr__(self) -> str:
        return f"<RechargeTicket {self.code} {self.plan} {self.scans_granted}sc status={self.status}>"
