"""System liquidity account for simulated markets.

Revision ID: 0008_beginner_trading_liquidity
Revises: 0007_mfa_production_auth
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008_beginner_trading_liquidity"
down_revision: str | None = "0007_mfa_production_auth"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
  with op.batch_alter_table("users") as batch_op:
    batch_op.add_column(sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.false()))
    batch_op.create_index("ix_users_is_system", ["is_system"])


def downgrade() -> None:
  with op.batch_alter_table("users") as batch_op:
    batch_op.drop_index("ix_users_is_system")
    batch_op.drop_column("is_system")
