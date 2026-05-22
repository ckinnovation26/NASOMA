"""Modèles marketing in-app + SAV 2 tiers.

Cf. docs/strategie_Nasoma.md § 3 quinquies :
- Canal marketing permanent (tous états, même FROZEN/ARCHIVED)
- SAV : IA pour tous, escalade humaine seulement pour ACTIVE
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum

from app.db.session import Base


# ──────────────────────────────────────────────
#  Marketing
# ──────────────────────────────────────────────
class MarketingAudience(str, enum.Enum):
    ALL = "all"                          # tous états
    ACTIVE = "active"                    # comptes actifs seulement
    INACTIVE = "inactive"                # grace + frozen
    GRACE = "grace"
    FROZEN = "frozen"
    PLAN_MONTHLY = "plan:monthly"
    PLAN_WEEKLY = "plan:weekly"
    PLAN_DISCOVERY = "plan:discovery"


class MarketingMessage(Base):
    """Broadcast in-app — visible peu importe l'account_state."""

    __tablename__ = "marketing_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    cta_label: Mapped[str | None] = mapped_column(String(40), nullable=True)
    cta_url: Mapped[str | None] = mapped_column(String(240), nullable=True)
    audience: Mapped[MarketingAudience] = mapped_column(
        Enum(MarketingAudience), default=MarketingAudience.ALL, nullable=False, index=True
    )
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    priority: Mapped[int] = mapped_column(SmallInteger, default=3, nullable=False)
    # 1 = banner top, 5 = feed bottom
    language: Mapped[str] = mapped_column(String(10), default="fr", nullable=False)
    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<MarketingMessage {self.id} {self.audience} pri={self.priority}>"


# ──────────────────────────────────────────────
#  SAV (Support)
# ──────────────────────────────────────────────
class ConversationStatus(str, enum.Enum):
    AI_ONLY = "ai_only"                  # IA gère
    AWAITING_HUMAN = "awaiting_human"    # escalade demandée, en attente d'agent
    WITH_HUMAN = "with_human"            # agent humain en cours
    CLOSED = "closed"


class MessageSender(str, enum.Enum):
    USER = "user"
    AI = "ai"
    AGENT = "agent"


class SupportConversation(Base):
    """Une conversation SAV — IA pour tous, humain ACTIVE only."""

    __tablename__ = "support_conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus),
        default=ConversationStatus.AI_ONLY,
        nullable=False,
        index=True,
    )
    # Snapshot account_state au moment de l'ouverture
    user_account_state_snapshot: Mapped[str] = mapped_column(String(16), nullable=False)
    assigned_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    satisfaction_rating: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True
    )  # 1-5


class SupportMessage(Base):
    """Message dans une conversation SAV."""

    __tablename__ = "support_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("support_conversations.id"),
        nullable=False,
        index=True,
    )
    sender_type: Mapped[MessageSender] = mapped_column(Enum(MessageSender), nullable=False)
    sender_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    ai_cost_usd: Mapped[float | None] = mapped_column(
        Numeric(6, 4), nullable=True
    )  # tracking Gemini
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
