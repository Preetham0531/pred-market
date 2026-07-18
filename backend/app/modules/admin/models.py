from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.security import utc_now
from app.db.base import Base, UUIDPrimaryKeyMixin


class AdminReview(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "admin_reviews"

  suggestion_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("market_suggestions.id"), nullable=True)
  draft_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("market_drafts.id"), nullable=True)
  market_id: Mapped[str | None] = mapped_column(String(120), ForeignKey("markets.id"), nullable=True)
  title: Mapped[str] = mapped_column(Text, nullable=False)
  category: Mapped[str] = mapped_column(String(160), nullable=False)
  status: Mapped[str] = mapped_column(String(80), nullable=False)
  risk: Mapped[str] = mapped_column(String(40), nullable=False)
  submitted_by: Mapped[str] = mapped_column(String(160), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
  resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
