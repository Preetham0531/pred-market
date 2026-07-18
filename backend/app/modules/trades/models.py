from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin
from app.modules.markets.models import Market, Outcome


class Trade(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "trades"

  market_id: Mapped[str] = mapped_column(String(120), ForeignKey("markets.id"), nullable=False, index=True)
  outcome_id: Mapped[str] = mapped_column(String(36), ForeignKey("outcomes.id"), nullable=False)
  price_minor: Mapped[int] = mapped_column(Integer, nullable=False)
  quantity: Mapped[int] = mapped_column(Integer, nullable=False)
  buyer_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
  seller_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
  yes_order_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("orders.id"), nullable=True)
  no_order_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("orders.id"), nullable=True)
  buy_order_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("orders.id"), nullable=True)
  sell_order_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("orders.id"), nullable=True)
  status: Mapped[str] = mapped_column(String(40), nullable=False, default="EXECUTED")
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

  market: Mapped[Market] = relationship("Market")
  outcome: Mapped[Outcome] = relationship("Outcome")
