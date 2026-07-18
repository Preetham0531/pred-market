from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.security import utc_now
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
  __tablename__ = "users"

  email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
  password_hash: Mapped[str] = mapped_column(Text, nullable=False)
  display_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
  status: Mapped[str] = mapped_column(String(40), nullable=False, default="ACTIVE", index=True)
  kyc_status: Mapped[str] = mapped_column(String(40), nullable=False, default="NOT_STARTED")
  jurisdiction_code: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
  email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
  failed_login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
  last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

  roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")


class UserRole(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "user_roles"
  __table_args__ = (UniqueConstraint("user_id", "role", name="uq_user_roles_user_role"),)

  user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
  role: Mapped[str] = mapped_column(String(40), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

  user: Mapped[User] = relationship("User", back_populates="roles")
