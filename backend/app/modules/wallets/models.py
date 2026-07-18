from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.modules.users.models import User


class Wallet(UUIDPrimaryKeyMixin, TimestampMixin, Base):
  __tablename__ = "wallets"
  __table_args__ = (UniqueConstraint("user_id", "currency", name="uq_wallet_user_currency"),)

  user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
  currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
  available_balance_minor: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  locked_balance_minor: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

  user: Mapped[User] = relationship("User")


class LedgerAccount(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "ledger_accounts"
  __table_args__ = (UniqueConstraint("owner_type", "owner_id", "account_type", "currency", name="uq_ledger_account_scope"),)

  owner_type: Mapped[str] = mapped_column(String(60), nullable=False)
  owner_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
  account_type: Mapped[str] = mapped_column(String(80), nullable=False)
  currency: Mapped[str] = mapped_column(String(3), nullable=False)
  name: Mapped[str] = mapped_column(Text, nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class LedgerTransaction(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "ledger_transactions"

  transaction_type: Mapped[str] = mapped_column(String(80), nullable=False)
  idempotency_key: Mapped[str | None] = mapped_column(String(160), nullable=True, unique=True)
  request_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
  reference_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
  reference_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
  metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

  entries: Mapped[list["LedgerEntry"]] = relationship("LedgerEntry", back_populates="transaction", cascade="all, delete-orphan")


class LedgerEntry(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "ledger_entries"

  transaction_id: Mapped[str] = mapped_column(String(36), ForeignKey("ledger_transactions.id"), nullable=False)
  account_id: Mapped[str] = mapped_column(String(36), ForeignKey("ledger_accounts.id"), nullable=False)
  side: Mapped[str] = mapped_column(String(20), nullable=False)
  amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
  currency: Mapped[str] = mapped_column(String(3), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

  transaction: Mapped[LedgerTransaction] = relationship("LedgerTransaction", back_populates="entries")
  account: Mapped[LedgerAccount] = relationship("LedgerAccount")
