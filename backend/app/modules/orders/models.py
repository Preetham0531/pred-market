from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.modules.markets.models import Market, Outcome
from app.modules.users.models import User


class Order(UUIDPrimaryKeyMixin, TimestampMixin, Base):
  __tablename__ = "orders"

  user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
  market_id: Mapped[str] = mapped_column(String(120), ForeignKey("markets.id"), nullable=False, index=True)
  outcome_id: Mapped[str] = mapped_column(String(36), ForeignKey("outcomes.id"), nullable=False, index=True)
  side: Mapped[str] = mapped_column(String(20), nullable=False)
  price_minor: Mapped[int] = mapped_column(Integer, nullable=False)
  quantity: Mapped[int] = mapped_column(Integer, nullable=False)
  filled_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  cancelled_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  locked_cash_minor: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  locked_shares: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  status: Mapped[str] = mapped_column(String(40), nullable=False)
  idempotency_key: Mapped[str | None] = mapped_column(String(160), nullable=True, unique=True)
  cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

  user: Mapped[User] = relationship("User")
  market: Mapped[Market] = relationship("Market")
  outcome: Mapped[Outcome] = relationship("Outcome")

  @property
  def remaining_quantity(self) -> int:
    return self.quantity - self.filled_quantity - self.cancelled_quantity
