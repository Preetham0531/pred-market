from datetime import datetime

from pydantic import BaseModel


class TradeResponse(BaseModel):
  id: str
  market_id: str
  outcome_id: str
  outcome: str
  price_minor: int
  quantity: int
  buyer_user_id: str
  seller_user_id: str | None
  status: str
  created_at: datetime


class TradePage(BaseModel):
  items: list[TradeResponse]
  next_cursor: str | None = None
