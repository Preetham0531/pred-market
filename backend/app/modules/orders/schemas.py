from datetime import datetime

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
  market_id: str
  outcome_id: str | None = None
  outcome: str | None = None
  side: str = Field(pattern="^(BUY|SELL)$")
  price_minor: int = Field(gt=0, le=99)
  quantity: int = Field(gt=0, le=100_000)


class OrderResponse(BaseModel):
  id: str
  user_id: str
  market_id: str
  outcome_id: str
  outcome: str
  side: str
  price_minor: int
  quantity: int
  filled_quantity: int
  cancelled_quantity: int
  remaining_quantity: int
  locked_cash_minor: int
  locked_shares: int
  status: str
  created_at: datetime
  updated_at: datetime
  cancelled_at: datetime | None


class OrderPage(BaseModel):
  items: list[OrderResponse]
  next_cursor: str | None = None
