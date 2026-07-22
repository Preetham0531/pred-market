"""MFA factors, recovery codes, and session assurance.

Revision ID: 0007_mfa_production_auth
Revises: 0006_market_issuance
Create Date: 2026-07-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007_mfa_production_auth"
down_revision: str | None = "0006_market_issuance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
  with op.batch_alter_table("auth_sessions") as batch_op:
    batch_op.add_column(sa.Column("mfa_verified_at", sa.DateTime(timezone=True), nullable=True))
    batch_op.add_column(sa.Column("mfa_method", sa.String(length=40), nullable=True))

  op.create_table(
    "user_mfa_factors",
    sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("factor_type", sa.String(length=40), nullable=False, server_default="TOTP"),
    sa.Column("label", sa.String(length=120), nullable=False, server_default="Authenticator app"),
    sa.Column("secret_ciphertext", sa.Text(), nullable=False),
    sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("last_used_step", sa.Integer(), nullable=True),
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
  )
  op.create_index("ix_user_mfa_factors_user_id", "user_mfa_factors", ["user_id"])

  op.create_table(
    "mfa_recovery_codes",
    sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("factor_id", sa.String(length=36), sa.ForeignKey("user_mfa_factors.id"), nullable=False),
    sa.Column("code_hash", sa.Text(), nullable=False),
    sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("id", sa.String(length=36), primary_key=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.UniqueConstraint("factor_id", "code_hash", name="uq_mfa_recovery_factor_code"),
  )
  op.create_index("ix_mfa_recovery_codes_user_id", "mfa_recovery_codes", ["user_id"])
  op.create_index("ix_mfa_recovery_codes_factor_id", "mfa_recovery_codes", ["factor_id"])


def downgrade() -> None:
  op.drop_index("ix_mfa_recovery_codes_factor_id", table_name="mfa_recovery_codes")
  op.drop_index("ix_mfa_recovery_codes_user_id", table_name="mfa_recovery_codes")
  op.drop_table("mfa_recovery_codes")
  op.drop_index("ix_user_mfa_factors_user_id", table_name="user_mfa_factors")
  op.drop_table("user_mfa_factors")
  with op.batch_alter_table("auth_sessions") as batch_op:
    batch_op.drop_column("mfa_method")
    batch_op.drop_column("mfa_verified_at")
