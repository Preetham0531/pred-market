from sqlalchemy import BigInteger, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.modules.markets.models import Market, Outcome
from app.modules.users.models import User


class Position(UUIDPrimaryKeyMixin, TimestampMixin, Base):
  __tablename__ = "positions"
  __table_args__ = (UniqueConstraint("user_id", "market_id", "outcome_id", name="uq_position_user_market_outcome"),)

  user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
  market_id: Mapped[str] = mapped_column(String(120), ForeignKey("markets.id"), nullable=False)
  outcome_id: Mapped[str] = mapped_column(String(36), ForeignKey("outcomes.id"), nullable=False)
  quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  locked_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  average_entry_price_minor: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  realized_pnl_minor: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  status: Mapped[str] = mapped_column(String(40), nullable=False, default="OPEN")

  user: Mapped[User] = relationship("User")
  market: Mapped[Market] = relationship("Market")
  outcome: Mapped[Outcome] = relationship("Outcome")
