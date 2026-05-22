"""KYC IdentityDocument + WhatsApp signup methods + user channel fields.

Revision ID: 0006_kyc_whatsapp
Revises: 0005_billing_video_assistance
Create Date: 2026-05-20 22:00:00

Ajoute :
- table identity_documents (CNI, passeport, acte de naissance scannés)
- enums documenttype, kycstatus
- nouveaux SignupMethod : WHATSAPP_VENDOR, WHATSAPP_DIASPORA
- colonnes users : kyc_status, preferred_otp_channel, app_installed, last_app_active_at
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_kyc_whatsapp"
down_revision: str | None = "0005_billing_video_assistance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ─── Étendre enum signupmethod ───
    op.execute(
        "ALTER TYPE signupmethod ADD VALUE IF NOT EXISTS 'whatsapp_vendor'"
    )
    op.execute(
        "ALTER TYPE signupmethod ADD VALUE IF NOT EXISTS 'whatsapp_diaspora'"
    )

    # ─── Nouveaux enums KYC ───
    document_type = sa.Enum(
        "cni",
        "passport",
        "birth_certificate",
        "school_card",
        name="documenttype",
    )
    kyc_status = sa.Enum(
        "not_verified",
        "pending",
        "verified",
        "rejected",
        name="kycstatus",
    )
    for enum in (document_type, kyc_status):
        enum.create(op.get_bind(), checkfirst=True)

    # ─── identity_documents ───
    op.create_table(
        "identity_documents",
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
        sa.Column("document_type", document_type, nullable=False),
        sa.Column("image_storage_key", sa.String(256), nullable=False),
        sa.Column("thumbnail_storage_key", sa.String(256), nullable=True),
        sa.Column("extracted_name", sa.String(120), nullable=True),
        sa.Column(
            "extracted_document_number_hash", sa.String(128), nullable=True
        ),
        sa.Column("extracted_birth_date", sa.String(10), nullable=True),
        sa.Column(
            "uploaded_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("uploaded_by_source", sa.String(40), nullable=False),
        sa.Column("verified_by_vendor_code", sa.String(40), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column(
            "kyc_status", kyc_status, nullable=False, server_default="pending"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_iddocs_tenant", "identity_documents", ["tenant_id"])
    op.create_index("ix_iddocs_user", "identity_documents", ["user_id"])
    op.create_index("ix_iddocs_status", "identity_documents", ["kyc_status"])

    # ─── users — nouvelles colonnes ───
    op.add_column(
        "users",
        sa.Column(
            "kyc_status",
            sa.String(20),
            nullable=False,
            server_default="not_verified",
        ),
    )
    op.create_index("ix_users_kyc_status", "users", ["kyc_status"])
    op.add_column(
        "users",
        sa.Column(
            "preferred_otp_channel",
            sa.String(20),
            nullable=False,
            server_default="whatsapp",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "app_installed",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )
    op.add_column(
        "users", sa.Column("last_app_active_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("users", "last_app_active_at")
    op.drop_column("users", "app_installed")
    op.drop_column("users", "preferred_otp_channel")
    op.drop_index("ix_users_kyc_status", "users")
    op.drop_column("users", "kyc_status")
    op.drop_table("identity_documents")
    for enum_name in ("kycstatus", "documenttype"):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
    # Note : on ne peut pas retirer 'whatsapp_vendor' / 'whatsapp_diaspora' de signupmethod
