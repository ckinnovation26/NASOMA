"""Marketing in-app + SAV 2 tiers.

Revision ID: 0009_marketing_support
Revises: 0008_spaced_repetition
Create Date: 2026-05-21 00:30:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009_marketing_support"
down_revision: str | None = "0008_spaced_repetition"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    marketing_audience = sa.Enum(
        "all",
        "active",
        "inactive",
        "grace",
        "frozen",
        "plan:monthly",
        "plan:weekly",
        "plan:discovery",
        name="marketingaudience",
    )
    conversation_status = sa.Enum(
        "ai_only", "awaiting_human", "with_human", "closed", name="conversationstatus"
    )
    message_sender = sa.Enum("user", "ai", "agent", name="messagesender")
    for e in (marketing_audience, conversation_status, message_sender):
        e.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "marketing_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("cta_label", sa.String(40), nullable=True),
        sa.Column("cta_url", sa.String(240), nullable=True),
        sa.Column("audience", marketing_audience, nullable=False, server_default="all"),
        sa.Column("push_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("priority", sa.SmallInteger(), nullable=False, server_default="3"),
        sa.Column("language", sa.String(10), nullable=False, server_default="fr"),
        sa.Column(
            "starts_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_marketing_tenant", "marketing_messages", ["tenant_id"])
    op.create_index("ix_marketing_audience", "marketing_messages", ["audience"])

    op.create_table(
        "support_conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "status", conversation_status, nullable=False, server_default="ai_only"
        ),
        sa.Column("user_account_state_snapshot", sa.String(16), nullable=False),
        sa.Column("assigned_agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "opened_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("satisfaction_rating", sa.SmallInteger(), nullable=True),
    )
    op.create_index("ix_support_tenant", "support_conversations", ["tenant_id"])
    op.create_index("ix_support_user", "support_conversations", ["user_id"])
    op.create_index("ix_support_status", "support_conversations", ["status"])

    op.create_table(
        "support_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("support_conversations.id"),
            nullable=False,
        ),
        sa.Column("sender_type", message_sender, nullable=False),
        sa.Column("sender_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("ai_cost_usd", sa.Numeric(6, 4), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_messages_conv", "support_messages", ["conversation_id"])


def downgrade() -> None:
    op.drop_table("support_messages")
    op.drop_table("support_conversations")
    op.drop_table("marketing_messages")
    for e in ("messagesender", "conversationstatus", "marketingaudience"):
        op.execute(f"DROP TYPE IF EXISTS {e}")
