"""Modèle OtpChallenge — défis OTP en cours et historiques.

Un OTP a 3 fonctions simultanées (cf. strategie_Nasoma.md § 3 quater) :
  1. Mot de passe (combiné au phone identifiant)
  2. Preuve de paiement
  3. Token de session (durée définie par le plan)

Types :
  - SMS_FIRST_SIGNUP   : OTP envoyé par SMS Firebase pour la 1ère inscription (3 scans / 7j)
  - VENDOR_TICKET      : OTP imprimé sur ticket physique vendeur
  - DIASPORA_PORTAL    : OTP affiché sur écran portail diaspora
  - RECOVERY           : OTP de récupération généré sur demande (gel)
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Enum

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.users import User


class OtpType(str, enum.Enum):
    SMS_FIRST_SIGNUP = "sms_first_signup"
    VENDOR_TICKET = "vendor_ticket"
    DIASPORA_PORTAL = "diaspora_portal"
    RECOVERY = "recovery"


class OtpStatus(str, enum.Enum):
    PENDING = "pending"          # généré, non consommé, non expiré
    CONSUMED = "consumed"        # utilisé avec succès (login OK)
    EXPIRED = "expired"          # délai dépassé sans consommation
    INVALIDATED = "invalidated"  # invalidé par un nouvel OTP plus récent


class OtpChallenge(Base):
    __tablename__ = "otp_challenges"

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
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,                              # null avant que l'user soit créé (1ère inscription)
        index=True,
    )
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    code_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    otp_type: Mapped[OtpType] = mapped_column(Enum(OtpType), nullable=False)
    status: Mapped[OtpStatus] = mapped_column(
        Enum(OtpStatus),
        default=OtpStatus.PENDING,
        nullable=False,
        index=True,
    )

    # Liens optionnels (pour OTP vendeur)
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id"),
        nullable=True,
    )
    recharge_ticket_code: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Sécurité
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    device_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user: Mapped[User | None] = relationship(back_populates="otp_challenges")

    def __repr__(self) -> str:
        return f"<OtpChallenge {self.id} {self.phone} type={self.otp_type} status={self.status}>"
