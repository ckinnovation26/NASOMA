"""Vendors model + DetectionType enum + scans.detection columns.

Revision ID: 0004_vendors_detection
Revises: 0003_fallback_assistance
Create Date: 2026-05-20 18:00:00

Ajoute :
- table vendors (avec GPS, vendor_type, status, training)
- enum detectiontype
- colonnes scans.detection_type, scans.detection_details
- enums vendortype, vendorstatus
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_vendors_detection"
down_revision: str | None = "0003_fallback_assistance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ─── Enums vendors ───
    vendor_type = sa.Enum(
        "kiosque",
        "school",
        "diaspora_portal",
        "agent",
        name="vendortype",
    )
    vendor_status = sa.Enum(
        "active", "inactive", "suspended", name="vendorstatus"
    )
    detection_type = sa.Enum(
        "success",
        "image_quality_low",
        "ocr_no_text",
        "no_school_work",
        "handwriting_illegible",
        "wrong_page",
        "concept_mapping_failed",
        "ocr_error",
        "network_error",
        name="detectiontype",
    )
    for enum in (vendor_type, vendor_status, detection_type):
        enum.create(op.get_bind(), checkfirst=True)

    # ─── vendors ───
    op.create_table(
        "vendors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column("code", sa.String(40), unique=True, nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("vendor_type", vendor_type, nullable=False),
        sa.Column("status", vendor_status, nullable=False, server_default="active"),
        sa.Column("contact_phone", sa.String(20), nullable=False),
        sa.Column("contact_email", sa.String(120), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("address_line", sa.String(255), nullable=True),
        sa.Column("city", sa.String(80), nullable=True),
        sa.Column("island", sa.String(40), nullable=True),
        sa.Column(
            "can_provide_assistance",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
        sa.Column(
            "is_trained_level1", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("trained_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "commission_percent", sa.Float(), nullable=False, server_default="15"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_vendors_tenant", "vendors", ["tenant_id"])
    op.create_index("ix_vendors_code", "vendors", ["code"], unique=True)
    op.create_index("ix_vendors_status", "vendors", ["status"])
    op.create_index("ix_vendors_city", "vendors", ["city"])

    # ─── scans.detection_type + detection_details ───
    op.add_column(
        "scans",
        sa.Column("detection_type", detection_type, nullable=True),
    )
    op.add_column(
        "scans",
        sa.Column("detection_details", postgresql.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("scans", "detection_details")
    op.drop_column("scans", "detection_type")
    op.drop_table("vendors")

    for enum_name in ("detectiontype", "vendorstatus", "vendortype"):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
