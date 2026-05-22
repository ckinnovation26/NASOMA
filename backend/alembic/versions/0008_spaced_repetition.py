"""Spaced Repetition — révision espacée (Moat #6).

Revision ID: 0008_spaced_repetition
Revises: 0007_indicators
Create Date: 2026-05-20 23:55:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_spaced_repetition"
down_revision: str | None = "0007_indicators"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    review_status = sa.Enum(
        "scheduled", "completed", "failed", "skipped", name="reviewstatus"
    )
    review_outcome = sa.Enum(
        "retained", "forgotten", "partial", name="reviewoutcome"
    )
    for e in (review_status, review_outcome):
        e.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "spaced_reviews",
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
        sa.Column(
            "concept_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("concepts.id"),
            nullable=False,
        ),
        sa.Column("scheduled_for", sa.Date(), nullable=False),
        sa.Column("interval_days", sa.SmallInteger(), nullable=False),
        sa.Column("status", review_status, nullable=False, server_default="scheduled"),
        sa.Column("outcome", review_outcome, nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("mastery_before", sa.Float(), nullable=True),
        sa.Column("mastery_after", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_reviews_tenant", "spaced_reviews", ["tenant_id"])
    op.create_index("ix_reviews_student", "spaced_reviews", ["student_id"])
    op.create_index("ix_reviews_concept", "spaced_reviews", ["concept_id"])
    op.create_index(
        "ix_reviews_due",
        "spaced_reviews",
        ["scheduled_for", "status"],
    )


def downgrade() -> None:
    op.drop_table("spaced_reviews")
    for e in ("reviewoutcome", "reviewstatus"):
        op.execute(f"DROP TYPE IF EXISTS {e}")
