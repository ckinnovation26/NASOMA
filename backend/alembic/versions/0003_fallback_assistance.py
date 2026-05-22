"""Fallback context + Vendor assistance + retry tracking on scans.

Revision ID: 0003_fallback_assistance
Revises: 0002_pedagogy_scans
Create Date: 2026-05-20 16:00:00

Ajoute :
- fallback_contexts (modal parent étape 2)
- vendor_assistance_requests (étape 3 recurrence)
- Colonnes retry_of_scan_id + retry_count + parent_chose_continue_without_rescan sur scans
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_fallback_assistance"
down_revision: str | None = "0002_pedagogy_scans"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ─── Enums ───
    assistance_reason = sa.Enum(
        "camera_defective",
        "photo_taking_skill",
        "homework_really_illegible",
        "repeat_failures",
        "unknown",
        name="assistancereason",
    )
    assistance_status = sa.Enum(
        "pending",
        "notified",
        "contacted",
        "resolved",
        "declined",
        "expired",
        name="assistancestatus",
    )
    for enum in (assistance_reason, assistance_status):
        enum.create(op.get_bind(), checkfirst=True)

    # ─── Colonnes retry sur scans ───
    op.add_column(
        "scans",
        sa.Column(
            "retry_of_scan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scans.id"),
            nullable=True,
        ),
    )
    op.add_column(
        "scans",
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "scans",
        sa.Column(
            "parent_chose_continue_without_rescan",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )

    # ─── fallback_contexts ───
    op.create_table(
        "fallback_contexts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column(
            "scan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scans.id"),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("subject_code", sa.String(20), nullable=False),
        sa.Column("grade_level", sa.String(8), nullable=False),
        sa.Column("recent_grade", sa.Numeric(5, 2), nullable=True),
        sa.Column("max_grade", sa.Numeric(5, 2), nullable=True, server_default="20"),
        sa.Column("parent_comment", sa.String(500), nullable=True),
        sa.Column("extracted_keywords", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_fbctx_tenant", "fallback_contexts", ["tenant_id"])
    op.create_index("ix_fbctx_scan", "fallback_contexts", ["scan_id"])
    op.create_index("ix_fbctx_student", "fallback_contexts", ["student_id"])

    # ─── vendor_assistance_requests ───
    op.create_table(
        "vendor_assistance_requests",
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
        sa.Column("vendor_id", sa.String(40), nullable=True),
        sa.Column("reason", assistance_reason, nullable=False),
        sa.Column(
            "failed_scans_count_7d", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("status", assistance_status, nullable=False, server_default="pending"),
        sa.Column(
            "courtesy_rescan_granted",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("notes_internal", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("notified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("contacted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_assist_tenant", "vendor_assistance_requests", ["tenant_id"])
    op.create_index("ix_assist_user", "vendor_assistance_requests", ["user_id"])
    op.create_index("ix_assist_vendor", "vendor_assistance_requests", ["vendor_id"])
    op.create_index("ix_assist_status", "vendor_assistance_requests", ["status"])


def downgrade() -> None:
    op.drop_table("vendor_assistance_requests")
    op.drop_table("fallback_contexts")
    op.drop_column("scans", "parent_chose_continue_without_rescan")
    op.drop_column("scans", "retry_count")
    op.drop_column("scans", "retry_of_scan_id")

    for enum_name in ("assistancestatus", "assistancereason"):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
