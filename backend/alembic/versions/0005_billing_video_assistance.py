"""Billing post-paid : OutstandingBill + VideoAssistanceSession + User home GPS.

Revision ID: 0005_billing_video_assistance
Revises: 0004_vendors_detection
Create Date: 2026-05-20 20:00:00

Ajoute :
- table outstanding_bills (factures dues)
- table video_assistance_sessions (assistance vidéo payante 200 KMF/10min)
- colonnes users.home_latitude, home_longitude, home_city, home_island
- enums billkind, billstatus, videoassistancestatus
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_billing_video_assistance"
down_revision: str | None = "0004_vendors_detection"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ─── Enums ───
    bill_kind = sa.Enum(
        "video_assistance", "late_fee", "manual", name="billkind"
    )
    bill_status = sa.Enum(
        "outstanding", "settled", "waived", "disputed", name="billstatus"
    )
    video_status = sa.Enum(
        "requested",
        "disclosed",
        "in_progress",
        "completed",
        "canceled",
        "refused_not_active",
        name="videoassistancestatus",
    )
    for enum in (bill_kind, bill_status, video_status):
        enum.create(op.get_bind(), checkfirst=True)

    # ─── outstanding_bills (créé avant video_assistance_sessions car FK) ───
    op.create_table(
        "outstanding_bills",
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
        sa.Column("kind", bill_kind, nullable=False),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("amount_kmf", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="KMF"),
        sa.Column("status", bill_status, nullable=False, server_default="outstanding"),
        sa.Column("source_video_session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "settled_via_payment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("payments.id"),
            nullable=True,
        ),
        sa.Column("settled_via_vendor_id", sa.String(40), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("grace_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_bills_tenant", "outstanding_bills", ["tenant_id"])
    op.create_index("ix_bills_user", "outstanding_bills", ["user_id"])
    op.create_index("ix_bills_status", "outstanding_bills", ["status"])

    # ─── video_assistance_sessions ───
    op.create_table(
        "video_assistance_sessions",
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
        sa.Column("account_state_at_request", sa.String(16), nullable=False),
        sa.Column(
            "status", video_status, nullable=False, server_default="requested"
        ),
        sa.Column(
            "rate_kmf_per_10min", sa.Integer(), nullable=False, server_default="200"
        ),
        sa.Column("disclosed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("disclosure_text", sa.Text(), nullable=True),
        sa.Column(
            "user_consent", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("agent_name", sa.String(120), nullable=True),
        sa.Column("video_room_url", sa.String(255), nullable=True),
        sa.Column("video_provider", sa.String(40), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("billed_minutes_rounded_up", sa.Integer(), nullable=True),
        sa.Column("billed_amount_kmf", sa.Integer(), nullable=True),
        sa.Column(
            "outstanding_bill_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("outstanding_bills.id"),
            nullable=True,
        ),
        sa.Column("notes_agent", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_vasession_tenant", "video_assistance_sessions", ["tenant_id"])
    op.create_index("ix_vasession_user", "video_assistance_sessions", ["user_id"])
    op.create_index("ix_vasession_status", "video_assistance_sessions", ["status"])

    # ─── users home location columns ───
    op.add_column("users", sa.Column("home_latitude", sa.Float(), nullable=True))
    op.add_column("users", sa.Column("home_longitude", sa.Float(), nullable=True))
    op.add_column("users", sa.Column("home_city", sa.String(80), nullable=True))
    op.add_column("users", sa.Column("home_island", sa.String(40), nullable=True))
    op.create_index("ix_users_home_city", "users", ["home_city"])


def downgrade() -> None:
    op.drop_index("ix_users_home_city", "users")
    op.drop_column("users", "home_island")
    op.drop_column("users", "home_city")
    op.drop_column("users", "home_longitude")
    op.drop_column("users", "home_latitude")
    op.drop_table("video_assistance_sessions")
    op.drop_table("outstanding_bills")

    for enum_name in ("videoassistancestatus", "billstatus", "billkind"):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
