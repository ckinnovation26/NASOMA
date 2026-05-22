"""Initial auth schema — tenants, users (with lifecycle), otp_challenges, subscriptions, payments, recharge_tickets.

Revision ID: 0001_initial_auth
Revises:
Create Date: 2026-05-20 12:00:00

Cf. docs/architecture.md + docs/strategie_Nasoma.md § 3 quater.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "0001_initial_auth"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ─── Extensions Postgres ───
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # ─── tenants ───
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(8), unique=True, nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("default_locale", sa.String(10), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("momo_providers", postgresql.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Seed du tenant KM (Comores) — MVP single-tenant
    op.execute(
        """
        INSERT INTO tenants (id, code, name, default_locale, currency, momo_providers)
        VALUES (
            uuid_generate_v4(),
            'KM',
            'Union des Comores',
            'fr-KM',
            'KMF',
            '["hollo", "mvola"]'::json
        )
        """,
    )

    # ─── Enums ───
    user_role = sa.Enum("student", "parent", "teacher", "school_admin", name="userrole")
    account_state = sa.Enum("active", "grace", "frozen", "archived", name="accountstate")
    signup_method = sa.Enum(
        "sms_firebase", "sms_at", "vendor", "diaspora_portal", name="signupmethod"
    )
    otp_type = sa.Enum(
        "sms_first_signup", "vendor_ticket", "diaspora_portal", "recovery", name="otptype"
    )
    otp_status = sa.Enum("pending", "consumed", "expired", "invalidated", name="otpstatus")
    plan = sa.Enum(
        "discovery", "daily", "weekly", "monthly", "school_b2b", name="subscriptionplan"
    )
    sub_status = sa.Enum("active", "grace", "expired", "canceled", name="subscriptionstatus")
    pay_provider = sa.Enum(
        "hollo",
        "mvola",
        "mpesa",
        "orange_money",
        "airtel_money",
        "stripe",
        "physical_ticket",
        "school_b2b",
        name="paymentprovider",
    )
    pay_status = sa.Enum(
        "pending", "success", "failed", "refunded", "canceled", name="paymentstatus"
    )
    ticket_status = sa.Enum(
        "generated", "redeemed", "expired", "canceled", name="ticketstatus"
    )
    for enum in (
        user_role,
        account_state,
        signup_method,
        otp_type,
        otp_status,
        plan,
        sub_status,
        pay_provider,
        pay_status,
        ticket_status,
    ):
        enum.create(op.get_bind(), checkfirst=True)

    # ─── users ───
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column("phone", sa.String(20), unique=True, nullable=False),
        sa.Column("email", sa.String(120), nullable=True),
        sa.Column("role", user_role, nullable=False),
        sa.Column("locale", sa.String(10), nullable=False, server_default="fr-KM"),
        sa.Column("full_name", sa.String(120), nullable=True),
        sa.Column("grade_level", sa.String(8), nullable=True),
        sa.Column("encrypted_pii", sa.LargeBinary(), nullable=True),
        sa.Column(
            "account_state", account_state, nullable=False, server_default="active"
        ),
        sa.Column("credit_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_valid_otp_hash", sa.String(128), nullable=True),
        sa.Column("last_valid_otp_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("state_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "first_signup_phone_verified",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("first_signup_method", signup_method, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_phone", "users", ["phone"])
    op.create_index("ix_users_account_state", "users", ["account_state"])
    op.create_index("ix_users_credit_expires_at", "users", ["credit_expires_at"])

    # ─── otp_challenges ───
    op.create_table(
        "otp_challenges",
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
            nullable=True,
        ),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("code_hash", sa.String(128), nullable=False),
        sa.Column("otp_type", otp_type, nullable=False),
        sa.Column("status", otp_status, nullable=False, server_default="pending"),
        sa.Column(
            "subscription_id", postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column("recharge_ticket_code", sa.String(20), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("device_id", sa.String(64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_otp_tenant", "otp_challenges", ["tenant_id"])
    op.create_index("ix_otp_user", "otp_challenges", ["user_id"])
    op.create_index("ix_otp_phone", "otp_challenges", ["phone"])
    op.create_index("ix_otp_status", "otp_challenges", ["status"])

    # ─── payments ───
    op.create_table(
        "payments",
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
        sa.Column("amount_local", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="KMF"),
        sa.Column("amount_usd", sa.Numeric(10, 2), nullable=True),
        sa.Column("provider", pay_provider, nullable=False),
        sa.Column("provider_ref", sa.String(120), unique=True, nullable=True),
        sa.Column("status", pay_status, nullable=False, server_default="pending"),
        sa.Column("vendor_id", sa.String(40), nullable=True),
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_payments_tenant", "payments", ["tenant_id"])
    op.create_index("ix_payments_user", "payments", ["user_id"])
    op.create_index("ix_payments_status", "payments", ["status"])

    # ─── subscriptions ───
    op.create_table(
        "subscriptions",
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
        sa.Column("plan", plan, nullable=False),
        sa.Column("status", sub_status, nullable=False, server_default="active"),
        sa.Column("scans_remaining", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "scans_granted_total", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("auto_renew", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "origin_payment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("payments.id"),
            nullable=True,
        ),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancel_reason", sa.String(120), nullable=True),
    )
    op.create_index("ix_subscriptions_tenant", "subscriptions", ["tenant_id"])
    op.create_index("ix_subscriptions_user", "subscriptions", ["user_id"])
    op.create_index("ix_subscriptions_status", "subscriptions", ["status"])
    op.create_index("ix_subscriptions_expires", "subscriptions", ["expires_at"])

    # FK retardée otp_challenges.subscription_id (cycle de définition)
    op.create_foreign_key(
        "fk_otp_subscription",
        "otp_challenges",
        "subscriptions",
        ["subscription_id"],
        ["id"],
    )

    # ─── recharge_tickets ───
    op.create_table(
        "recharge_tickets",
        sa.Column("code", sa.String(20), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column("code_hmac", sa.String(64), nullable=False),
        sa.Column("plan", plan, nullable=False),
        sa.Column("scans_granted", sa.SmallInteger(), nullable=False),
        sa.Column("duration_days", sa.SmallInteger(), nullable=False),
        sa.Column("vendor_id", sa.String(40), nullable=False),
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("batch_id", sa.String(40), nullable=False),
        sa.Column("target_phone", sa.String(20), nullable=False),
        sa.Column("status", ticket_status, nullable=False, server_default="generated"),
        sa.Column(
            "redeemed_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("redeemed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "sold_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_tickets_tenant", "recharge_tickets", ["tenant_id"])
    op.create_index("ix_tickets_vendor", "recharge_tickets", ["vendor_id"])
    op.create_index("ix_tickets_batch", "recharge_tickets", ["batch_id"])
    op.create_index("ix_tickets_phone", "recharge_tickets", ["target_phone"])
    op.create_index("ix_tickets_status", "recharge_tickets", ["status"])
    op.create_index("ix_tickets_expires", "recharge_tickets", ["expires_at"])


def downgrade() -> None:
    op.drop_table("recharge_tickets")
    op.drop_constraint("fk_otp_subscription", "otp_challenges", type_="foreignkey")
    op.drop_table("subscriptions")
    op.drop_table("payments")
    op.drop_table("otp_challenges")
    op.drop_table("users")
    op.drop_table("tenants")

    for enum_name in (
        "ticketstatus",
        "paymentstatus",
        "paymentprovider",
        "subscriptionstatus",
        "subscriptionplan",
        "otpstatus",
        "otptype",
        "signupmethod",
        "accountstate",
        "userrole",
    ):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
