"""professional auth impersonation

Revision ID: 0005_professional_auth
Revises: 0004_watchlist
Create Date: 2026-07-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_professional_auth"
down_revision: str | None = "0004_watchlist"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
  op.create_table(
    "admin_impersonation_sessions",
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("auth_session_id", sa.String(length=36), sa.ForeignKey("auth_sessions.id"), nullable=False),
    sa.Column("actor_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("target_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("mode", sa.String(length=40), nullable=False, server_default="READ_ONLY"),
    sa.Column("reason", sa.Text(), nullable=False),
    sa.Column("ip_hash", sa.Text(), nullable=True),
    sa.Column("user_agent", sa.Text(), nullable=True),
    sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("ended_reason", sa.Text(), nullable=True),
  )
  op.create_index("ix_admin_impersonation_sessions_auth_session_id", "admin_impersonation_sessions", ["auth_session_id"])
  op.create_index("ix_admin_impersonation_sessions_actor_user_id", "admin_impersonation_sessions", ["actor_user_id"])
  op.create_index("ix_admin_impersonation_sessions_target_user_id", "admin_impersonation_sessions", ["target_user_id"])


def downgrade() -> None:
  op.drop_index("ix_admin_impersonation_sessions_target_user_id", table_name="admin_impersonation_sessions")
  op.drop_index("ix_admin_impersonation_sessions_actor_user_id", table_name="admin_impersonation_sessions")
  op.drop_index("ix_admin_impersonation_sessions_auth_session_id", table_name="admin_impersonation_sessions")
  op.drop_table("admin_impersonation_sessions")
