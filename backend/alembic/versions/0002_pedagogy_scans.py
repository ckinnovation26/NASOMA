"""Pedagogy + scans + sessions — Sprint 2.

Revision ID: 0002_pedagogy_scans
Revises: 0001_initial_auth
Create Date: 2026-05-20 14:00:00

Ajoute :
- subjects (matières)
- concepts + concept_prerequisites (Knowledge Graph DAG)
- student_concept_mastery (BKT)
- scans + diagnostics + scan_archives (Moat #1)
- exercise_templates
- sessions + session_answers
- Plan THREE_DAY ajouté à subscriptionplan
- ScanStatus DONE_WITH_FALLBACK ajouté
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_pedagogy_scans"
down_revision: str | None = "0001_initial_auth"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ─── Ajouts aux enums existants ───
    op.execute("ALTER TYPE subscriptionplan ADD VALUE IF NOT EXISTS 'three_day'")

    # ─── Nouveaux enums ───
    scan_status = sa.Enum(
        "pending",
        "processing",
        "done",
        "done_with_fallback",
        "failed",
        name="scanstatus",
    )
    ocr_provider = sa.Enum(
        "mlkit_local",
        "cloud_vision",
        "gemini_flash",
        "gemini_flash_8b",
        name="ocrprovider",
    )
    exercise_type = sa.Enum("mcq", "fill_blank", "short_text", "drag_drop", name="exercisetype")
    session_status = sa.Enum(
        "in_progress", "completed", "abandoned", name="sessionstatus"
    )
    for enum in (scan_status, ocr_provider, exercise_type, session_status):
        enum.create(op.get_bind(), checkfirst=True)

    # ─── subjects ───
    op.create_table(
        "subjects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column("code", sa.String(20), unique=True, nullable=False),
        sa.Column("name", sa.String(60), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_subjects_tenant", "subjects", ["tenant_id"])

    # Seed 4 matières par défaut pour le tenant KM
    op.execute(
        """
        INSERT INTO subjects (id, tenant_id, code, name)
        SELECT uuid_generate_v4(), t.id, code, name FROM tenants t,
        (VALUES
            ('MATH', 'Mathématiques'),
            ('FR', 'Français'),
            ('AR', 'Arabe coranique'),
            ('SCI', 'Sciences')
        ) AS s(code, name)
        WHERE t.code = 'KM'
        """,
    )

    # ─── concepts ───
    op.create_table(
        "concepts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "subject_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("subjects.id"),
            nullable=False,
        ),
        sa.Column("code", sa.String(40), unique=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("name_shikomori", sa.String(200), nullable=True),
        sa.Column("grade_level", sa.String(8), nullable=False),
        sa.Column("difficulty", sa.SmallInteger(), nullable=False),
        sa.Column("estimated_minutes", sa.SmallInteger(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("curriculum_refs", postgresql.JSON(), nullable=True),
        sa.Column("common_errors", postgresql.JSON(), nullable=True),
        sa.Column("example_exercise", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_concepts_subject", "concepts", ["subject_id"])
    op.create_index("ix_concepts_code", "concepts", ["code"])
    op.create_index("ix_concepts_grade", "concepts", ["grade_level"])

    # ─── concept_prerequisites (DAG edges) ───
    op.create_table(
        "concept_prerequisites",
        sa.Column(
            "concept_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("concepts.id"),
            primary_key=True,
        ),
        sa.Column(
            "prereq_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("concepts.id"),
            primary_key=True,
        ),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
    )

    # ─── student_concept_mastery (BKT) ───
    op.create_table(
        "student_concept_mastery",
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
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column("mastery_probability", sa.Float(), nullable=False, server_default="0.1"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("successes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "consecutive_successes", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "failures_last_7_days", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("last_practiced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "last_updated",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_mastery_tenant_student", "student_concept_mastery", ["tenant_id", "student_id"]
    )

    # ─── scans ───
    op.create_table(
        "scans",
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
            "subject_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("subjects.id"),
            nullable=True,
        ),
        sa.Column("image_storage_key", sa.String(256), nullable=False),
        sa.Column("thumbnail_storage_key", sa.String(256), nullable=True),
        sa.Column("image_phash", sa.String(64), nullable=True),
        sa.Column("image_size_bytes", sa.Integer(), nullable=True),
        sa.Column("status", scan_status, nullable=False, server_default="pending"),
        sa.Column("ocr_raw_text", sa.Text(), nullable=True),
        sa.Column("ocr_provider", ocr_provider, nullable=True),
        sa.Column("ocr_confidence", sa.Float(), nullable=True),
        sa.Column("ai_cost_usd", sa.Float(), nullable=True, server_default="0"),
        sa.Column("ai_tokens_input", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("ai_tokens_output", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("grade_level", sa.String(8), nullable=True),
        sa.Column(
            "cached_from_phash", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("fallback_used", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("fallback_reason", sa.String(120), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_scans_tenant", "scans", ["tenant_id"])
    op.create_index("ix_scans_student", "scans", ["student_id"])
    op.create_index("ix_scans_status", "scans", ["status"])
    op.create_index("ix_scans_phash", "scans", ["image_phash"])
    op.create_index(
        "ix_scans_student_created", "scans", ["student_id", "created_at"]
    )

    # ─── diagnostics ───
    op.create_table(
        "diagnostics",
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
            unique=True,
            nullable=False,
        ),
        sa.Column("detected_errors", postgresql.JSON(), nullable=False),
        sa.Column(
            "concepts_affected",
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            nullable=True,
        ),
        sa.Column("summary_text", sa.Text(), nullable=True),
        sa.Column(
            "total_exercises_detected", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("correct_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("incorrect_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_diagnostics_tenant", "diagnostics", ["tenant_id"])

    # ─── scan_archives ───
    op.create_table(
        "scan_archives",
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
            "scan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scans.id"),
            nullable=False,
        ),
        sa.Column("image_storage_key", sa.String(256), nullable=False),
        sa.Column("thumbnail_storage_key", sa.String(256), nullable=True),
        sa.Column("ocr_text", sa.Text(), nullable=True),
        sa.Column("diagnostic_summary", sa.Text(), nullable=True),
        sa.Column("exercises_detected", postgresql.JSON(), nullable=True),
        sa.Column(
            "concepts_touched",
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            nullable=True,
        ),
        sa.Column("scan_quality_score", sa.Float(), nullable=True),
        sa.Column("subject", sa.String(20), nullable=True),
        sa.Column("grade_level", sa.String(8), nullable=True),
        sa.Column(
            "is_archived_consent", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_archives_tenant_student", "scan_archives", ["tenant_id", "student_id"]
    )

    # ─── exercise_templates ───
    op.create_table(
        "exercise_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column(
            "concept_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("concepts.id"),
            nullable=False,
        ),
        sa.Column("type", exercise_type, nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("template_json", postgresql.JSON(), nullable=False),
        sa.Column("locale", sa.String(10), nullable=False, server_default="fr-KM"),
        sa.Column("validated_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("generated_by", sa.String(40), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_templates_concept", "exercise_templates", ["concept_id"]
    )

    # ─── sessions ───
    op.create_table(
        "sessions",
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
            "diagnostic_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("diagnostics.id"),
            nullable=True,
        ),
        sa.Column(
            "target_concept_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("concepts.id"),
            nullable=False,
        ),
        sa.Column(
            "status", session_status, nullable=False, server_default="in_progress"
        ),
        sa.Column("exercise_order", postgresql.JSON(), nullable=True),
        sa.Column("success_rate", sa.Float(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_sessions_student", "sessions", ["student_id"])
    op.create_index("ix_sessions_concept", "sessions", ["target_concept_id"])

    # ─── session_answers ───
    op.create_table(
        "session_answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sessions.id"),
            nullable=False,
        ),
        sa.Column(
            "exercise_template_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exercise_templates.id"),
            nullable=False,
        ),
        sa.Column("student_answer", sa.String(500), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("mastery_before", sa.Float(), nullable=True),
        sa.Column("mastery_after", sa.Float(), nullable=True),
        sa.Column(
            "answered_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_answers_session", "session_answers", ["session_id"])


def downgrade() -> None:
    op.drop_table("session_answers")
    op.drop_table("sessions")
    op.drop_table("exercise_templates")
    op.drop_table("scan_archives")
    op.drop_table("diagnostics")
    op.drop_table("scans")
    op.drop_table("student_concept_mastery")
    op.drop_table("concept_prerequisites")
    op.drop_table("concepts")
    op.drop_table("subjects")

    for enum_name in (
        "sessionstatus",
        "exercisetype",
        "ocrprovider",
        "scanstatus",
    ):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")

    # Note : impossible de retirer 'three_day' de subscriptionplan en Postgres
