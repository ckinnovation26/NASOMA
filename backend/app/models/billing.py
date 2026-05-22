"""Modèles facturation post-paid : OutstandingBill + VideoAssistanceSession.

Principes (cf. docs/strategie_Nasoma.md) :
- Assistance vidéo payante 200 KMF / 10 min
- Post-paid : facturée à la prochaine recharge (debt)
- Disclosure obligatoire avant démarrage
- Réservé aux comptes ACTIVE (vérification au start)
- Visible dans dashboard vendeur dès saisie du numéro client
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime, Enum


from app.db.session import Base


class BillKind(str, enum.Enum):
    """Type de facture en attente."""

    VIDEO_ASSISTANCE = "video_assistance"
    LATE_FEE = "late_fee"                 # frais de retard
    MANUAL = "manual"                     # ajustement manuel admin


class BillStatus(str, enum.Enum):
    OUTSTANDING = "outstanding"           # dû, non réglé
    SETTLED = "settled"                   # réglé par le client
    WAIVED = "waived"                     # offert / annulé
    DISPUTED = "disputed"                 # contestation


class VideoAssistanceStatus(str, enum.Enum):
    REQUESTED = "requested"               # demande créée, en attente d'agent
    DISCLOSED = "disclosed"               # tarification confirmée par le user
    IN_PROGRESS = "in_progress"           # session active
    COMPLETED = "completed"               # finie, durée calculée
    CANCELED = "canceled"                 # annulée avant disclosure
    REFUSED_NOT_ACTIVE = "refused_not_active"  # refusée car compte non-actif


class VideoAssistanceSession(Base):
    """Session d'assistance vidéo (Zoom/Meet/Twilio).

    Coût : 200 KMF / 10 min, facturé à la prochaine recharge.
    Réservé aux comptes ACTIVE (vérifié au start).
    """

    __tablename__ = "video_assistance_sessions"

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

    # Snapshot account_state au moment de la demande (audit/débogage)
    account_state_at_request: Mapped[str] = mapped_column(String(16), nullable=False)

    status: Mapped[VideoAssistanceStatus] = mapped_column(
        Enum(VideoAssistanceStatus),
        default=VideoAssistanceStatus.REQUESTED,
        nullable=False,
        index=True,
    )

    # Tarification (snapshot — peut changer dans le futur)
    rate_kmf_per_10min: Mapped[int] = mapped_column(Integer, default=200, nullable=False)
    disclosed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    disclosure_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_consent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Agent assigné
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    agent_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    video_room_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    video_provider: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # 'twilio_video' | 'jitsi' | 'meet'

    # Durée + facturation
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    billed_minutes_rounded_up: Mapped[int | None] = mapped_column(Integer, nullable=True)
    billed_amount_kmf: Mapped[int | None] = mapped_column(Integer, nullable=True)
    outstanding_bill_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("outstanding_bills.id"),
        nullable=True,
    )

    notes_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<VideoAssistanceSession {self.id} status={self.status} "
            f"duration={self.duration_seconds}s>"
        )


class OutstandingBill(Base):
    """Facture en attente de règlement (post-paid).

    Visible dans le dashboard vendeur dès la saisie du numéro client.
    Doit être réglée AVANT toute nouvelle recharge.
    """

    __tablename__ = "outstanding_bills"

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

    kind: Mapped[BillKind] = mapped_column(Enum(BillKind), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount_kmf: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="KMF", nullable=False)

    status: Mapped[BillStatus] = mapped_column(
        Enum(BillStatus),
        default=BillStatus.OUTSTANDING,
        nullable=False,
        index=True,
    )

    # Lien vers ce qui a généré la facture
    source_video_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Règlement
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    settled_via_payment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payments.id"),
        nullable=True,
    )
    settled_via_vendor_id: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # Échéance / pénalité
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    grace_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<OutstandingBill {self.id} {self.kind} {self.amount_kmf} {self.currency} "
            f"status={self.status}>"
        )
