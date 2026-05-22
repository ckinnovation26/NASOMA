"""Indicateurs CT/MT/LT + mastery snapshots.

Revision ID: 0007_indicators
Revises: 0006_kyc_whatsapp
Create Date: 2026-05-20 23:30:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_indicators"
down_revision: str | None = "0006_kyc_whatsapp"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    indicator_horizon = sa.Enum("ct", "mt", "lt", name="indicatorhorizon")
    indicator_horizon.create(op.get_bind(), checkfirst=True)

    # ─── mastery_snapshots ───
    op.create_table(
        "mastery_snapshots",
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            primary_key=True,
        ),
        sa.Column(
            "concept_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("concepts.id"),
            primary_key=True,
        ),
        sa.Column("snapshot_date", sa.Date(), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column("mastery_probability", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_snapshots_tenant_date",
        "mastery_snapshots",
        ["tenant_id", "snapshot_date"],
    )
    op.create_index(
        "ix_snapshots_student_date",
        "mastery_snapshots",
        ["student_id", "snapshot_date"],
    )

    # ─── student_indicators ───
    op.create_table(
        "student_indicators",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("horizon", indicator_horizon, nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("metrics", postgresql.JSON(), nullable=False),
        sa.Column(
            "recommendations", postgresql.JSON(), nullable=False, server_default="[]"
        ),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_indicators_tenant", "student_indicators", ["tenant_id"]
    )
    op.create_index(
        "ix_indicators_student_horizon",
        "student_indicators",
        ["student_id", "horizon"],
    )


def downgrade() -> None:
    op.drop_table("student_indicators")
    op.drop_table("mastery_snapshots")
    op.execute("DROP TYPE IF EXISTS indicatorhorizon")
