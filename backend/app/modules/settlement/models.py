from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin
from app.modules.markets.models import Market, Outcome


class ResolutionProposal(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "resolution_proposals"

  market_id: Mapped[str] = mapped_column(String(120), ForeignKey("markets.id"), nullable=False)
  winning_outcome_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("outcomes.id"), nullable=True)
  result: Mapped[str] = mapped_column(String(80), nullable=False)
  reason: Mapped[str] = mapped_column(Text, nullable=False)
  maker_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
  checker_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
  status: Mapped[str] = mapped_column(String(40), nullable=False, default="PENDING")
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
  approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

  market: Mapped[Market] = relationship("Market")
  winning_outcome: Mapped[Outcome | None] = relationship("Outcome")


class Settlement(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "settlements"

  market_id: Mapped[str] = mapped_column(String(120), ForeignKey("markets.id"), nullable=False, unique=True)
  resolution_proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("resolution_proposals.id"), nullable=False)
  status: Mapped[str] = mapped_column(String(40), nullable=False)
  idempotency_key: Mapped[str | None] = mapped_column(String(160), nullable=True, unique=True)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
  completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

  items: Mapped[list["SettlementItem"]] = relationship("SettlementItem", back_populates="settlement", cascade="all, delete-orphan")


class SettlementItem(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "settlement_items"

  settlement_id: Mapped[str] = mapped_column(String(36), ForeignKey("settlements.id"), nullable=False)
  user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
  position_id: Mapped[str] = mapped_column(String(36), ForeignKey("positions.id"), nullable=False)
  payout_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

  settlement: Mapped[Settlement] = relationship("Settlement", back_populates="items")
