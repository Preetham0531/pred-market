from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin


class MarketAnalytics(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "market_analytics"

  market_id: Mapped[str] = mapped_column(String(120), ForeignKey("markets.id"), nullable=False, unique=True, index=True)
  outcome_metrics_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
  best_bid: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
  best_ask: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
  last_trade: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
  spread: Mapped[float | None] = mapped_column(Float, nullable=True)
  volume_24h: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  total_volume: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  open_interest: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  liquidity_depth: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  price_change_24h: Mapped[float] = mapped_column(Float, nullable=False, default=0)
  computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
  is_stale: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class CategoryAnalytics(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "category_analytics"

  category_slug: Mapped[str] = mapped_column(String(80), ForeignKey("categories.slug"), nullable=False, unique=True, index=True)
  active_markets: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  volume_24h: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  top_markets_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
  top_movers_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
  average_spread: Mapped[float | None] = mapped_column(Float, nullable=True)
  liquidity_depth: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  risk_alerts_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
  computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
  is_stale: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class UserAnalytics(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "user_analytics"

  user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True)
  available_cash: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  locked_cash: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  positions_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
  category_exposure_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
  market_exposure_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
  unrealized_pnl: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  realized_pnl: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  max_payout: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  max_loss: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
  computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
  is_stale: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
