from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class WatchlistItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
  __tablename__ = "watchlist_items"
  __table_args__ = (UniqueConstraint("user_id", "market_id", name="uq_watchlist_user_market"),)

  user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
  market_id: Mapped[str] = mapped_column(String(120), ForeignKey("markets.id"), nullable=False, index=True)

  market = relationship("Market")
