from datetime import datetime
from typing import Any

from pydantic import BaseModel


class MarketAnalyticsResponse(BaseModel):
  market_id: str
  outcome_metrics: list[dict[str, Any]]
  best_bid: int | None
  best_ask: int | None
  last_trade: int | None
  spread: float | None
  volume_24h: int
  total_volume: int
  open_interest: int
  liquidity_depth: int
  price_change_24h: float
  computed_at: datetime
  is_stale: bool


class UserAnalyticsResponse(BaseModel):
  user_id: str
  available_cash: int
  locked_cash: int
  positions: list[dict[str, Any]]
  category_exposure: list[dict[str, Any]]
  market_exposure: list[dict[str, Any]]
  unrealized_pnl: int
  realized_pnl: int
  max_payout: int
  max_loss: int
  computed_at: datetime
  is_stale: bool


class CategoryAnalyticsResponse(BaseModel):
  category_slug: str
  active_markets: int
  volume_24h: int
  top_markets: list[dict[str, Any]]
  top_movers: list[dict[str, Any]]
  average_spread: float | None
  liquidity_depth: int
  risk_alerts: list[str]
  computed_at: datetime
  is_stale: bool


class RecomputeResponse(BaseModel):
  status: str
  markets: int
  categories: int
  users: int
