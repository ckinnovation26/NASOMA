"""Modèle User — élèves, parents, enseignants, school_admin.

Roles principaux (cf. §22 BP CHECK constraint) :
  - student
  - parent
  - teacher
  - school_admin

Roles internes (custom claims JWT, hors base) :
  - support (lecture seule, anonymisé)
  - admin (accès complet, audit log obligatoire)

Cycle de vie compte (cf. docs/strategie_Nasoma.md § 3 quater) :
  active → grace (30j) → frozen (12 mois) → archived
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, LargeBinary, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.otp_challenges import OtpChallenge
    from app.models.payments import Payment
    from app.models.subscriptions import Subscription
    from app.models.tenants import Tenant


class UserRole(str, enum.Enum):
    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"
    SCHOOL_ADMIN = "school_admin"


class AccountState(str, enum.Enum):
    """Cycle de vie du compte (modèle ligne téléphonique)."""

    ACTIVE = "active"        # crédit > 0 OU jours_restants > 0
    GRACE = "grace"          # 30j après expiration : lecture seule
    FROZEN = "frozen"        # > 30j : pas d'accès direct, export RGPD sur demande
    ARCHIVED = "archived"    # > 365j : cold storage + anonymisation J+395


class SignupMethod(str, enum.Enum):
    """Comment l'utilisateur s'est inscrit (1ère fois)."""

    WHATSAPP_VENDOR = "whatsapp_vendor"         # vendeur enregistre + WhatsApp OTP (PRIMARY)
    WHATSAPP_DIASPORA = "whatsapp_diaspora"     # diaspora enregistre + WhatsApp OTP (PRIMARY)
    SMS_FIREBASE = "sms_firebase"               # fallback Firebase Phone (rare)
    SMS_AT = "sms_at"                           # fallback Africa's Talking
    VENDOR = "vendor"                           # ancien flow sans WhatsApp (legacy)
    DIASPORA_PORTAL = "diaspora_portal"         # ancien flow diaspora (legacy)


class User(Base):
    __tablename__ = "users"

    # ─── Identité ───
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
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    locale: Mapped[str] = mapped_column(String(10), default="fr-KM")
    full_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    grade_level: Mapped[str | None] = mapped_column(String(8), nullable=True)
    encrypted_pii: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    # ─── Cycle de vie compte (modèle ligne téléphonique) ───
    account_state: Mapped[AccountState] = mapped_column(
        Enum(AccountState),
        default=AccountState.ACTIVE,
        nullable=False,
        index=True,
    )
    credit_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    last_valid_otp_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_valid_otp_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    state_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ─── Première inscription ───
    first_signup_phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    first_signup_method: Mapped[SignupMethod | None] = mapped_column(
        Enum(SignupMethod),
        nullable=True,
    )
    # KYC : pièce d'identité scannée par vendeur ou uploadée par diaspora
    kyc_status: Mapped[str] = mapped_column(
        String(20),
        default="not_verified",
        nullable=False,
        index=True,
    )
    # Canal préféré pour OTP (whatsapp 1ère fois, push après)
    preferred_otp_channel: Mapped[str] = mapped_column(
        String(20),
        default="whatsapp",
        nullable=False,
    )
    app_installed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_app_active_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ─── Localisation (pour recommandation vendeur proche, cf. diaspora flow) ───
    # GPS du domicile de l'élève (avec consentement RGPD), utilisé pour recommander
    # un vendeur proche en cas d'achat diaspora ou d'assistance physique.
    home_latitude: Mapped[float | None] = mapped_column(nullable=True)
    home_longitude: Mapped[float | None] = mapped_column(nullable=True)
    home_city: Mapped[str | None] = mapped_column(String(80), nullable=True)
    home_island: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # ─── Timestamps ───
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    last_active_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ─── Relations ───
    tenant: Mapped[Tenant] = relationship(back_populates="users")
    otp_challenges: Mapped[list[OtpChallenge]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    subscriptions: Mapped[list[Subscription]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    payments: Mapped[list[Payment]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.id} {self.role} {self.phone} state={self.account_state}>"
