"""watchlist persistence

Revision ID: 0004_watchlist
Revises: 0003_phase_7
Create Date: 2026-07-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_watchlist"
down_revision: str | None = "0003_phase_7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
  op.create_table(
    "watchlist_items",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("market_id", sa.String(length=120), sa.ForeignKey("markets.id"), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.UniqueConstraint("user_id", "market_id", name="uq_watchlist_user_market"),
  )
  op.create_index("ix_watchlist_items_user_id", "watchlist_items", ["user_id"])
  op.create_index("ix_watchlist_items_market_id", "watchlist_items", ["market_id"])


def downgrade() -> None:
  op.drop_index("ix_watchlist_items_market_id", table_name="watchlist_items")
  op.drop_index("ix_watchlist_items_user_id", table_name="watchlist_items")
  op.drop_table("watchlist_items")
