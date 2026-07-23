from typing import Any

from pydantic import BaseModel


class CategoryResponse(BaseModel):
  slug: str
  name: str
  short_name: str
  description: str
  active_markets: int
  volume_24h: int
  total_volume: int
  risk: str
  icon_tone: str
  focus: list[str]


class CategoryList(BaseModel):
  items: list[CategoryResponse]
  next_cursor: str | None = None


class OutcomeResponse(BaseModel):
  id: str
  label: str
  price: int
  probability: int


class MarketQuote(BaseModel):
  yes_bid: int | None
  yes_ask: int | None
  no_bid: int | None
  no_ask: int | None
  last_trade: int | None
  spread: int | None


class MarketListItem(BaseModel):
  id: str
  title: str
  category_slug: str
  subcategory: str
  market_type: str
  status: str
  close_time: str
  source: str
  rule_summary: str
  probability: int
  change_24h: float
  volume_24h: int
  total_volume: int
  liquidity: int
  spread: float
  traders: int
  outcomes: list[OutcomeResponse]
  risk_notes: list[str]
  quote: MarketQuote


class MarketDetail(MarketListItem):
  price_history: list[dict[str, Any]]
  order_book: dict[str, Any]
  recent_trades: list[dict[str, Any]]


class PaginatedMarkets(BaseModel):
  items: list[MarketListItem]
  next_cursor: str | None = None


class OrderBookResponse(BaseModel):
  market_id: str
  sequence: int
  updated_at: str
  quote: MarketQuote
  order_book: dict[str, Any]


class PriceHistoryResponse(BaseModel):
  market_id: str
  points: list[dict[str, Any]]
