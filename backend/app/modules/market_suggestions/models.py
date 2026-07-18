from typing import Any

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.modules.users.models import User


class MarketSuggestion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
  __tablename__ = "market_suggestions"

  submitted_by_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
  category_slug: Mapped[str] = mapped_column(String(80), ForeignKey("categories.slug"), nullable=False)
  market_type: Mapped[str] = mapped_column(String(60), nullable=False)
  question: Mapped[str] = mapped_column(Text, nullable=False)
  outcomes_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
  source: Mapped[str] = mapped_column(Text, nullable=False)
  resolution_rule: Mapped[str] = mapped_column(Text, nullable=False)
  status: Mapped[str] = mapped_column(String(60), nullable=False, default="PENDING_REVIEW")
  checks_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

  submitted_by: Mapped[User] = relationship("User")
