"""phase 1 3 initial schema

Revision ID: 0001_phase_1_3
Revises:
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_phase_1_3"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
  op.create_table(
    "users",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("email", sa.String(length=320), nullable=False),
    sa.Column("password_hash", sa.Text(), nullable=False),
    sa.Column("display_name", sa.String(length=160), nullable=True),
    sa.Column("status", sa.String(length=40), nullable=False, server_default="ACTIVE"),
    sa.Column("kyc_status", sa.String(length=40), nullable=False, server_default="NOT_STARTED"),
    sa.Column("jurisdiction_code", sa.String(length=16), nullable=True),
    sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("failed_login_count", sa.Integer(), nullable=False, server_default="0"),
    sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
    sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
  )
  op.create_index("ix_users_email", "users", [sa.text("lower(email)")], unique=True)
  op.create_index("ix_users_status", "users", ["status"])
  op.create_index("ix_users_jurisdiction_code", "users", ["jurisdiction_code"])

  op.create_table(
    "user_roles",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("role", sa.String(length=40), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.UniqueConstraint("user_id", "role", name="uq_user_roles_user_role"),
  )

  op.create_table(
    "auth_sessions",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("refresh_token_hash", sa.Text(), nullable=False, unique=True),
    sa.Column("csrf_token_hash", sa.Text(), nullable=False),
    sa.Column("user_agent", sa.Text(), nullable=True),
    sa.Column("ip_hash", sa.Text(), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("revoked_reason", sa.Text(), nullable=True),
  )
  op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])

  op.create_table(
    "email_verification_tokens",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("token_hash", sa.Text(), nullable=False, unique=True),
    sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
  )

  op.create_table(
    "password_reset_tokens",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("token_hash", sa.Text(), nullable=False, unique=True),
    sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
  )

  op.create_table(
    "audit_logs",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("event_type", sa.String(length=80), nullable=False),
    sa.Column("actor_user_id", sa.String(length=36), nullable=True),
    sa.Column("target_user_id", sa.String(length=36), nullable=True),
    sa.Column("request_id", sa.String(length=80), nullable=True),
    sa.Column("ip_hash", sa.Text(), nullable=True),
    sa.Column("user_agent", sa.Text(), nullable=True),
    sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
  )
  op.create_index("ix_audit_logs_event_type", "audit_logs", ["event_type"])
  op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])

  op.create_table(
    "categories",
    sa.Column("slug", sa.String(length=80), primary_key=True),
    sa.Column("name", sa.String(length=160), nullable=False),
    sa.Column("short_name", sa.String(length=80), nullable=False),
    sa.Column("description", sa.Text(), nullable=False),
    sa.Column("risk", sa.String(length=40), nullable=False),
    sa.Column("icon_tone", sa.String(length=40), nullable=False),
    sa.Column("focus_json", sa.JSON(), nullable=False, server_default="[]"),
    sa.Column("active_markets", sa.Integer(), nullable=False, server_default="0"),
    sa.Column("volume_24h", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("total_volume", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
  )

  op.create_table(
    "markets",
    sa.Column("id", sa.String(length=120), primary_key=True),
    sa.Column("title", sa.Text(), nullable=False),
    sa.Column("category_slug", sa.String(length=80), sa.ForeignKey("categories.slug"), nullable=False),
    sa.Column("subcategory", sa.String(length=120), nullable=False),
    sa.Column("market_type", sa.String(length=60), nullable=False),
    sa.Column("status", sa.String(length=60), nullable=False),
    sa.Column("close_time", sa.String(length=120), nullable=False),
    sa.Column("source", sa.Text(), nullable=False),
    sa.Column("rule_summary", sa.Text(), nullable=False),
    sa.Column("probability", sa.Integer(), nullable=False),
    sa.Column("change_24h", sa.Float(), nullable=False, server_default="0"),
    sa.Column("volume_24h", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("total_volume", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("liquidity", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("spread", sa.Float(), nullable=False, server_default="0"),
    sa.Column("traders", sa.Integer(), nullable=False, server_default="0"),
    sa.Column("risk_notes_json", sa.JSON(), nullable=False, server_default="[]"),
    sa.Column("price_history_json", sa.JSON(), nullable=False, server_default="[]"),
    sa.Column("order_book_json", sa.JSON(), nullable=False, server_default="{}"),
    sa.Column("recent_trades_json", sa.JSON(), nullable=False, server_default="[]"),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
  )
  op.create_index("ix_markets_category_slug", "markets", ["category_slug"])
  op.create_index("ix_markets_status", "markets", ["status"])

  op.create_table(
    "market_rules",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("market_id", sa.String(length=120), sa.ForeignKey("markets.id"), nullable=False, unique=True),
    sa.Column("resolution_rule", sa.Text(), nullable=False),
    sa.Column("void_policy", sa.Text(), nullable=False),
    sa.Column("source_url", sa.Text(), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
  )

  op.create_table(
    "outcomes",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("market_id", sa.String(length=120), sa.ForeignKey("markets.id"), nullable=False),
    sa.Column("label", sa.String(length=120), nullable=False),
    sa.Column("price", sa.Integer(), nullable=False),
    sa.Column("probability", sa.Integer(), nullable=False),
    sa.Column("status", sa.String(length=40), nullable=False, server_default="ACTIVE"),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.UniqueConstraint("market_id", "label", name="uq_outcomes_market_label"),
  )

  op.create_table(
    "oracle_evidence",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("market_id", sa.String(length=120), sa.ForeignKey("markets.id"), nullable=False),
    sa.Column("source_name", sa.String(length=160), nullable=False),
    sa.Column("source_url", sa.Text(), nullable=True),
    sa.Column("captured_payload_json", sa.JSON(), nullable=False, server_default="{}"),
    sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
  )

  op.create_table(
    "market_suggestions",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("submitted_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("category_slug", sa.String(length=80), sa.ForeignKey("categories.slug"), nullable=False),
    sa.Column("market_type", sa.String(length=60), nullable=False),
    sa.Column("question", sa.Text(), nullable=False),
    sa.Column("outcomes_json", sa.JSON(), nullable=False, server_default="[]"),
    sa.Column("source", sa.Text(), nullable=False),
    sa.Column("resolution_rule", sa.Text(), nullable=False),
    sa.Column("status", sa.String(length=60), nullable=False, server_default="PENDING_REVIEW"),
    sa.Column("checks_json", sa.JSON(), nullable=False, server_default="{}"),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
  )

  op.create_table(
    "admin_reviews",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("suggestion_id", sa.String(length=36), sa.ForeignKey("market_suggestions.id"), nullable=True),
    sa.Column("market_id", sa.String(length=120), sa.ForeignKey("markets.id"), nullable=True),
    sa.Column("title", sa.Text(), nullable=False),
    sa.Column("category", sa.String(length=160), nullable=False),
    sa.Column("status", sa.String(length=80), nullable=False),
    sa.Column("risk", sa.String(length=40), nullable=False),
    sa.Column("submitted_by", sa.String(length=160), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
  )


def downgrade() -> None:
  op.drop_table("admin_reviews")
  op.drop_table("market_suggestions")
  op.drop_table("oracle_evidence")
  op.drop_table("outcomes")
  op.drop_table("market_rules")
  op.drop_index("ix_markets_status", table_name="markets")
  op.drop_index("ix_markets_category_slug", table_name="markets")
  op.drop_table("markets")
  op.drop_table("categories")
  op.drop_index("ix_audit_logs_actor_user_id", table_name="audit_logs")
  op.drop_index("ix_audit_logs_event_type", table_name="audit_logs")
  op.drop_table("audit_logs")
  op.drop_table("password_reset_tokens")
  op.drop_table("email_verification_tokens")
  op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
  op.drop_table("auth_sessions")
  op.drop_table("user_roles")
  op.drop_index("ix_users_jurisdiction_code", table_name="users")
  op.drop_index("ix_users_status", table_name="users")
  op.drop_index("ix_users_email", table_name="users")
  op.drop_table("users")
