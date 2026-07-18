from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin


class RealtimeEvent(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "realtime_events"

  sequence: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True, index=True)
  event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
  channel: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
  scope_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
  scope_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
  market_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
  user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
  payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
  publish_status: Mapped[str] = mapped_column(String(40), nullable=False, default="PENDING", index=True)
  error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
  published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
