"""phase 4 6 trading schema

Revision ID: 0002_phase_4_6
Revises: 0001_phase_1_3
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_phase_4_6"
down_revision: str | None = "0001_phase_1_3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
  op.create_table(
    "wallets",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("currency", sa.String(length=3), nullable=False),
    sa.Column("available_balance_minor", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("locked_balance_minor", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.CheckConstraint("available_balance_minor >= 0", name="ck_wallet_available_nonnegative"),
    sa.CheckConstraint("locked_balance_minor >= 0", name="ck_wallet_locked_nonnegative"),
    sa.UniqueConstraint("user_id", "currency", name="uq_wallet_user_currency"),
  )
  op.create_index("ix_wallets_user_id", "wallets", ["user_id"])

  op.create_table(
    "ledger_accounts",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("owner_type", sa.String(length=60), nullable=False),
    sa.Column("owner_id", sa.String(length=120), nullable=True),
    sa.Column("account_type", sa.String(length=80), nullable=False),
    sa.Column("currency", sa.String(length=3), nullable=False),
    sa.Column("name", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.UniqueConstraint("owner_type", "owner_id", "account_type", "currency", name="uq_ledger_account_scope"),
  )

  op.create_table(
    "ledger_transactions",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("transaction_type", sa.String(length=80), nullable=False),
    sa.Column("idempotency_key", sa.String(length=160), nullable=True, unique=True),
    sa.Column("request_hash", sa.Text(), nullable=True),
    sa.Column("reference_type", sa.String(length=80), nullable=True),
    sa.Column("reference_id", sa.String(length=120), nullable=True),
    sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
  )

  op.create_table(
    "ledger_entries",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("transaction_id", sa.String(length=36), sa.ForeignKey("ledger_transactions.id"), nullable=False),
    sa.Column("account_id", sa.String(length=36), sa.ForeignKey("ledger_accounts.id"), nullable=False),
    sa.Column("side", sa.String(length=20), nullable=False),
    sa.Column("amount_minor", sa.BigInteger(), nullable=False),
    sa.Column("currency", sa.String(length=3), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.CheckConstraint("amount_minor > 0", name="ck_ledger_entry_amount_positive"),
  )

  op.create_table(
    "positions",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("market_id", sa.String(length=120), sa.ForeignKey("markets.id"), nullable=False),
    sa.Column("outcome_id", sa.String(length=36), sa.ForeignKey("outcomes.id"), nullable=False),
    sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"),
    sa.Column("locked_quantity", sa.Integer(), nullable=False, server_default="0"),
    sa.Column("average_entry_price_minor", sa.Integer(), nullable=False, server_default="0"),
    sa.Column("realized_pnl_minor", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("status", sa.String(length=40), nullable=False, server_default="OPEN"),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.CheckConstraint("quantity >= 0", name="ck_position_quantity_nonnegative"),
    sa.CheckConstraint("locked_quantity >= 0", name="ck_position_locked_nonnegative"),
    sa.UniqueConstraint("user_id", "market_id", "outcome_id", name="uq_position_user_market_outcome"),
  )

  op.create_table(
    "orders",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("market_id", sa.String(length=120), sa.ForeignKey("markets.id"), nullable=False),
    sa.Column("outcome_id", sa.String(length=36), sa.ForeignKey("outcomes.id"), nullable=False),
    sa.Column("side", sa.String(length=20), nullable=False),
    sa.Column("price_minor", sa.Integer(), nullable=False),
    sa.Column("quantity", sa.Integer(), nullable=False),
    sa.Column("filled_quantity", sa.Integer(), nullable=False, server_default="0"),
    sa.Column("cancelled_quantity", sa.Integer(), nullable=False, server_default="0"),
    sa.Column("locked_cash_minor", sa.BigInteger(), nullable=False, server_default="0"),
    sa.Column("locked_shares", sa.Integer(), nullable=False, server_default="0"),
    sa.Column("status", sa.String(length=40), nullable=False),
    sa.Column("idempotency_key", sa.String(length=160), nullable=True, unique=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint("price_minor > 0", name="ck_order_price_positive"),
    sa.CheckConstraint("quantity > 0", name="ck_order_quantity_positive"),
  )
  op.create_index("ix_orders_market_outcome_status", "orders", ["market_id", "outcome_id", "status"])
  op.create_index("ix_orders_user_id", "orders", ["user_id"])

  op.create_table(
    "trades",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("market_id", sa.String(length=120), sa.ForeignKey("markets.id"), nullable=False),
    sa.Column("outcome_id", sa.String(length=36), sa.ForeignKey("outcomes.id"), nullable=False),
    sa.Column("price_minor", sa.Integer(), nullable=False),
    sa.Column("quantity", sa.Integer(), nullable=False),
    sa.Column("buyer_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("seller_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
    sa.Column("yes_order_id", sa.String(length=36), sa.ForeignKey("orders.id"), nullable=True),
    sa.Column("no_order_id", sa.String(length=36), sa.ForeignKey("orders.id"), nullable=True),
    sa.Column("buy_order_id", sa.String(length=36), sa.ForeignKey("orders.id"), nullable=True),
    sa.Column("sell_order_id", sa.String(length=36), sa.ForeignKey("orders.id"), nullable=True),
    sa.Column("status", sa.String(length=40), nullable=False, server_default="EXECUTED"),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
  )
  op.create_index("ix_trades_market_id", "trades", ["market_id"])

  op.create_table(
    "resolution_proposals",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("market_id", sa.String(length=120), sa.ForeignKey("markets.id"), nullable=False),
    sa.Column("winning_outcome_id", sa.String(length=36), sa.ForeignKey("outcomes.id"), nullable=True),
    sa.Column("result", sa.String(length=80), nullable=False),
    sa.Column("reason", sa.Text(), nullable=False),
    sa.Column("maker_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("checker_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
    sa.Column("status", sa.String(length=40), nullable=False, server_default="PENDING"),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
  )

  op.create_table(
    "settlements",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("market_id", sa.String(length=120), sa.ForeignKey("markets.id"), nullable=False, unique=True),
    sa.Column("resolution_proposal_id", sa.String(length=36), sa.ForeignKey("resolution_proposals.id"), nullable=False),
    sa.Column("status", sa.String(length=40), nullable=False),
    sa.Column("idempotency_key", sa.String(length=160), nullable=True, unique=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
  )

  op.create_table(
    "settlement_items",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("settlement_id", sa.String(length=36), sa.ForeignKey("settlements.id"), nullable=False),
    sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("position_id", sa.String(length=36), sa.ForeignKey("positions.id"), nullable=False),
    sa.Column("payout_minor", sa.BigInteger(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
  )


def downgrade() -> None:
  op.drop_table("settlement_items")
  op.drop_table("settlements")
  op.drop_table("resolution_proposals")
  op.drop_index("ix_trades_market_id", table_name="trades")
  op.drop_table("trades")
  op.drop_index("ix_orders_user_id", table_name="orders")
  op.drop_index("ix_orders_market_outcome_status", table_name="orders")
  op.drop_table("orders")
  op.drop_table("positions")
  op.drop_table("ledger_entries")
  op.drop_table("ledger_transactions")
  op.drop_table("ledger_accounts")
  op.drop_index("ix_wallets_user_id", table_name="wallets")
  op.drop_table("wallets")
