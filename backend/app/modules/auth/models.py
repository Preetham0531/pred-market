from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin
from app.modules.users.models import User


class AuthSession(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "auth_sessions"

  user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
  refresh_token_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
  csrf_token_hash: Mapped[str] = mapped_column(Text, nullable=False)
  user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
  ip_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
  last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
  expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
  revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
  revoked_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

  user: Mapped[User] = relationship("User")


class AdminImpersonationSession(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "admin_impersonation_sessions"

  auth_session_id: Mapped[str] = mapped_column(String(36), ForeignKey("auth_sessions.id"), nullable=False, index=True)
  actor_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
  target_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
  mode: Mapped[str] = mapped_column(String(40), nullable=False, default="READ_ONLY")
  reason: Mapped[str] = mapped_column(Text, nullable=False)
  ip_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
  user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
  started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
  ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
  ended_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

  auth_session: Mapped[AuthSession] = relationship("AuthSession")
  actor_user: Mapped[User] = relationship("User", foreign_keys=[actor_user_id])
  target_user: Mapped[User] = relationship("User", foreign_keys=[target_user_id])


class EmailVerificationToken(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "email_verification_tokens"

  user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
  token_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
  expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
  used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class PasswordResetToken(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "password_reset_tokens"

  user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
  token_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
  expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
  used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
