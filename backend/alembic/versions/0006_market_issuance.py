"""market issuance data sources and drafts

Revision ID: 0006_market_issuance
Revises: 0005_professional_auth
Create Date: 2026-07-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_market_issuance"
down_revision: str | None = "0005_professional_auth"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
  op.create_table(
    "data_sources",
    sa.Column("name", sa.String(length=180), nullable=False),
    sa.Column("provider", sa.String(length=120), nullable=False),
    sa.Column("source_type", sa.String(length=60), nullable=False),
    sa.Column("category_slug", sa.String(length=80), sa.ForeignKey("categories.slug"), nullable=False),
    sa.Column("base_url", sa.Text(), nullable=False),
    sa.Column("license_status", sa.String(length=80), nullable=False),
    sa.Column("automation_level", sa.Integer(), nullable=False),
    sa.Column("refresh_schedule", sa.String(length=120), nullable=False),
    sa.Column("settlement_eligible", sa.Boolean(), nullable=False),
    sa.Column("discovery_eligible", sa.Boolean(), nullable=False),
    sa.Column("status", sa.String(length=60), nullable=False),
    sa.Column("health_status", sa.String(length=60), nullable=False),
    sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("config_json", sa.JSON(), nullable=False),
    sa.Column("notes", sa.Text(), nullable=True),
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.UniqueConstraint("name", "provider", name="uq_data_sources_name_provider"),
  )
  op.create_index("ix_data_sources_category_slug", "data_sources", ["category_slug"])

  op.create_table(
    "source_events",
    sa.Column("data_source_id", sa.String(length=36), sa.ForeignKey("data_sources.id"), nullable=False),
    sa.Column("category_slug", sa.String(length=80), sa.ForeignKey("categories.slug"), nullable=False),
    sa.Column("external_id", sa.String(length=240), nullable=True),
    sa.Column("title", sa.Text(), nullable=False),
    sa.Column("url", sa.Text(), nullable=True),
    sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("source_timestamp", sa.DateTime(timezone=True), nullable=True),
    sa.Column("raw_payload_json", sa.JSON(), nullable=False),
    sa.Column("content_hash", sa.String(length=128), nullable=False),
    sa.Column("dedupe_key", sa.String(length=260), nullable=False),
    sa.Column("credibility_score", sa.Integer(), nullable=False),
    sa.Column("ingestion_status", sa.String(length=60), nullable=False),
    sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.UniqueConstraint("data_source_id", "dedupe_key", name="uq_source_events_source_dedupe"),
  )
  op.create_index("ix_source_events_data_source_id", "source_events", ["data_source_id"])
  op.create_index("ix_source_events_category_slug", "source_events", ["category_slug"])
  op.create_index("ix_source_events_content_hash", "source_events", ["content_hash"])

  op.create_table(
    "market_drafts",
    sa.Column("origin", sa.String(length=40), nullable=False),
    sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
    sa.Column("suggestion_id", sa.String(length=36), sa.ForeignKey("market_suggestions.id"), nullable=True),
    sa.Column("listed_market_id", sa.String(length=120), sa.ForeignKey("markets.id"), nullable=True),
    sa.Column("category_slug", sa.String(length=80), sa.ForeignKey("categories.slug"), nullable=False),
    sa.Column("subcategory", sa.String(length=120), nullable=False),
    sa.Column("market_type", sa.String(length=60), nullable=False),
    sa.Column("question", sa.Text(), nullable=False),
    sa.Column("outcomes_json", sa.JSON(), nullable=False),
    sa.Column("close_time", sa.String(length=120), nullable=False),
    sa.Column("source", sa.Text(), nullable=False),
    sa.Column("resolution_rule", sa.Text(), nullable=False),
    sa.Column("void_policy", sa.Text(), nullable=False),
    sa.Column("settlement_source_id", sa.String(length=36), sa.ForeignKey("data_sources.id"), nullable=True),
    sa.Column("discovery_source_id", sa.String(length=36), sa.ForeignKey("data_sources.id"), nullable=True),
    sa.Column("status", sa.String(length=60), nullable=False),
    sa.Column("checks_json", sa.JSON(), nullable=False),
    sa.Column("risk_flags_json", sa.JSON(), nullable=False),
    sa.Column("ai_rationale", sa.Text(), nullable=True),
    sa.Column("confidence_score", sa.Integer(), nullable=True),
    sa.Column("admin_notes", sa.Text(), nullable=True),
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
  )
  op.create_index("ix_market_drafts_origin", "market_drafts", ["origin"])
  op.create_index("ix_market_drafts_category_slug", "market_drafts", ["category_slug"])
  op.create_index("ix_market_drafts_status", "market_drafts", ["status"])

  op.create_table(
    "market_draft_evidence",
    sa.Column("draft_id", sa.String(length=36), sa.ForeignKey("market_drafts.id"), nullable=False),
    sa.Column("source_event_id", sa.String(length=36), sa.ForeignKey("source_events.id"), nullable=True),
    sa.Column("data_source_id", sa.String(length=36), sa.ForeignKey("data_sources.id"), nullable=True),
    sa.Column("title", sa.Text(), nullable=False),
    sa.Column("url", sa.Text(), nullable=True),
    sa.Column("evidence_type", sa.String(length=60), nullable=False),
    sa.Column("snapshot_json", sa.JSON(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column("id", sa.String(length=36), primary_key=True),
  )
  op.create_index("ix_market_draft_evidence_draft_id", "market_draft_evidence", ["draft_id"])

  with op.batch_alter_table("admin_reviews") as batch_op:
    batch_op.add_column(sa.Column("draft_id", sa.String(length=36), nullable=True))
    batch_op.create_foreign_key("fk_admin_reviews_draft_id_market_drafts", "market_drafts", ["draft_id"], ["id"])


def downgrade() -> None:
  with op.batch_alter_table("admin_reviews") as batch_op:
    batch_op.drop_constraint("fk_admin_reviews_draft_id_market_drafts", type_="foreignkey")
    batch_op.drop_column("draft_id")
  op.drop_index("ix_market_draft_evidence_draft_id", table_name="market_draft_evidence")
  op.drop_table("market_draft_evidence")
  op.drop_index("ix_market_drafts_status", table_name="market_drafts")
  op.drop_index("ix_market_drafts_category_slug", table_name="market_drafts")
  op.drop_index("ix_market_drafts_origin", table_name="market_drafts")
  op.drop_table("market_drafts")
  op.drop_index("ix_source_events_content_hash", table_name="source_events")
  op.drop_index("ix_source_events_category_slug", table_name="source_events")
  op.drop_index("ix_source_events_data_source_id", table_name="source_events")
  op.drop_table("source_events")
  op.drop_index("ix_data_sources_category_slug", table_name="data_sources")
  op.drop_table("data_sources")
