"""phase 7 realtime analytics

Revision ID: 0003_phase_7
Revises: 0002_phase_4_6
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_phase_7"
down_revision: str | None = "0002_phase_4_6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
  op.create_table(
    "realtime_events",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("sequence", sa.BigInteger(), nullable=False, unique=True),
    sa.Column("event_type", sa.String(length=80), nullable=False),
    sa.Column("channel", sa.String(length=180), nullable=False),
    sa.Column("scope_type", sa.String(length=40), nullable=False),
    sa.Column("scope_id", sa.String(length=120), nullable=True),
    sa.Column("market_id", sa.String(length=120), nullable=True),
    sa.Column("user_id", sa.String(length=36), nullable=True),
    sa.Column("payload_json", sa.JSON(), nullable=False, server_default="{}"),
    sa.Column("publish_status", sa.String(length=40), nullable=False, server_default="PENDING"),
    sa.Column("error_message", sa.Text(), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
  )
  op.create_index("ix_realtime_events_sequence", "realtime_events", ["sequence"])
  op.create_index("ix_realtime_events_event_type", "realtime_events", ["event_type"])
  op.create_index("ix_realtime_events_channel", "realtime_events", ["channel"])
  op.create_index("ix_realtime_events_scope_type", "realtime_events", ["scope_type"])
  op.create_index("ix_realtime_events_scope_id", "realtime_events", ["scope_id"])
  op.create_index("ix_realtime_events_market_id", "realtime_events", ["market_id"])
  op.create_index("ix_realtime_events_user_id", "realtime_events", ["user_id"])
  op.create_index("ix_realtime_events_publish_status", "realtime_events", ["publish_status"])

  op.create_table(
    "market_analytics",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("market_id", sa.String(length=120), sa.ForeignKey("markets.id"), nullable=False, unique=True),
    sa.Column("outcome_metrics_json", sa.JSON(), nullable=False, server_default="[]"),
    sa.Column("best_bid", sa.BigInteger(), nullable=True),
    sa.Column("best_ask", sa.BigInteger(), nullable=True),
    sa.Column("last_trade", sa.BigInteger(), nullable=True),
    sa.Column("spread", sa.Float(), nullable=True),
    sa.Column("volume_24h", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("total_volume", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("open_interest", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("liquidity_depth", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("price_change_24h", sa.Float(), nullable=False, server_default="0"),
    sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("is_stale", sa.Boolean(), nullable=False, server_default=sa.false()),
  )
  op.create_index("ix_market_analytics_market_id", "market_analytics", ["market_id"])

  op.create_table(
    "category_analytics",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("category_slug", sa.String(length=80), sa.ForeignKey("categories.slug"), nullable=False, unique=True),
    sa.Column("active_markets", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("volume_24h", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("top_markets_json", sa.JSON(), nullable=False, server_default="[]"),
    sa.Column("top_movers_json", sa.JSON(), nullable=False, server_default="[]"),
    sa.Column("average_spread", sa.Float(), nullable=True),
    sa.Column("liquidity_depth", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("risk_alerts_json", sa.JSON(), nullable=False, server_default="[]"),
    sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("is_stale", sa.Boolean(), nullable=False, server_default=sa.false()),
  )
  op.create_index("ix_category_analytics_category_slug", "category_analytics", ["category_slug"])

  op.create_table(
    "user_analytics",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False, unique=True),
    sa.Column("available_cash", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("locked_cash", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("positions_json", sa.JSON(), nullable=False, server_default="[]"),
    sa.Column("category_exposure_json", sa.JSON(), nullable=False, server_default="[]"),
    sa.Column("market_exposure_json", sa.JSON(), nullable=False, server_default="[]"),
    sa.Column("unrealized_pnl", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("realized_pnl", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("max_payout", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("max_loss", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("is_stale", sa.Boolean(), nullable=False, server_default=sa.false()),
  )
  op.create_index("ix_user_analytics_user_id", "user_analytics", ["user_id"])


def downgrade() -> None:
  op.drop_index("ix_user_analytics_user_id", table_name="user_analytics")
  op.drop_table("user_analytics")
  op.drop_index("ix_category_analytics_category_slug", table_name="category_analytics")
  op.drop_table("category_analytics")
  op.drop_index("ix_market_analytics_market_id", table_name="market_analytics")
  op.drop_table("market_analytics")
  op.drop_index("ix_realtime_events_publish_status", table_name="realtime_events")
  op.drop_index("ix_realtime_events_user_id", table_name="realtime_events")
  op.drop_index("ix_realtime_events_market_id", table_name="realtime_events")
  op.drop_index("ix_realtime_events_scope_id", table_name="realtime_events")
  op.drop_index("ix_realtime_events_scope_type", table_name="realtime_events")
  op.drop_index("ix_realtime_events_channel", table_name="realtime_events")
  op.drop_index("ix_realtime_events_event_type", table_name="realtime_events")
  op.drop_index("ix_realtime_events_sequence", table_name="realtime_events")
  op.drop_table("realtime_events")
