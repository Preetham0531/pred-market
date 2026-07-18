from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin


class AuditLog(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "audit_logs"

  event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
  actor_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
  target_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
  request_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
  ip_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
  user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
  metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
