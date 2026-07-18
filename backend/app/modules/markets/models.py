from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, BigInteger, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Category(TimestampMixin, Base):
  __tablename__ = "categories"

  slug: Mapped[str] = mapped_column(String(80), primary_key=True)
  name: Mapped[str] = mapped_column(String(160), nullable=False)
  short_name: Mapped[str] = mapped_column(String(80), nullable=False)
  description: Mapped[str] = mapped_column(Text, nullable=False)
  risk: Mapped[str] = mapped_column(String(40), nullable=False)
  icon_tone: Mapped[str] = mapped_column(String(40), nullable=False)
  focus_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
  active_markets: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  volume_24h: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  total_volume: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

  markets: Mapped[list["Market"]] = relationship("Market", back_populates="category")


class Market(TimestampMixin, Base):
  __tablename__ = "markets"

  id: Mapped[str] = mapped_column(String(120), primary_key=True)
  title: Mapped[str] = mapped_column(Text, nullable=False)
  category_slug: Mapped[str] = mapped_column(String(80), ForeignKey("categories.slug"), nullable=False, index=True)
  subcategory: Mapped[str] = mapped_column(String(120), nullable=False)
  market_type: Mapped[str] = mapped_column(String(60), nullable=False)
  status: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
  close_time: Mapped[str] = mapped_column(String(120), nullable=False)
  source: Mapped[str] = mapped_column(Text, nullable=False)
  rule_summary: Mapped[str] = mapped_column(Text, nullable=False)
  probability: Mapped[int] = mapped_column(Integer, nullable=False)
  change_24h: Mapped[float] = mapped_column(Float, nullable=False, default=0)
  volume_24h: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  total_volume: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  liquidity: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  spread: Mapped[float] = mapped_column(Float, nullable=False, default=0)
  traders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  risk_notes_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
  price_history_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
  order_book_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
  recent_trades_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)

  category: Mapped[Category] = relationship("Category", back_populates="markets")
  outcomes: Mapped[list["Outcome"]] = relationship("Outcome", back_populates="market", cascade="all, delete-orphan")
  rule: Mapped["MarketRule | None"] = relationship("MarketRule", back_populates="market", uselist=False, cascade="all, delete-orphan")


class MarketRule(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "market_rules"

  market_id: Mapped[str] = mapped_column(String(120), ForeignKey("markets.id"), nullable=False, unique=True)
  resolution_rule: Mapped[str] = mapped_column(Text, nullable=False)
  void_policy: Mapped[str] = mapped_column(Text, nullable=False)
  source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

  market: Mapped[Market] = relationship("Market", back_populates="rule")


class Outcome(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "outcomes"
  __table_args__ = (UniqueConstraint("market_id", "label", name="uq_outcomes_market_label"),)

  market_id: Mapped[str] = mapped_column(String(120), ForeignKey("markets.id"), nullable=False)
  label: Mapped[str] = mapped_column(String(120), nullable=False)
  price: Mapped[int] = mapped_column(Integer, nullable=False)
  probability: Mapped[int] = mapped_column(Integer, nullable=False)
  status: Mapped[str] = mapped_column(String(40), nullable=False, default="ACTIVE")
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

  market: Mapped[Market] = relationship("Market", back_populates="outcomes")


class OracleEvidence(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "oracle_evidence"

  market_id: Mapped[str] = mapped_column(String(120), ForeignKey("markets.id"), nullable=False)
  source_name: Mapped[str] = mapped_column(String(160), nullable=False)
  source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
  captured_payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
  captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
