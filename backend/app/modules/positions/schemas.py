from pydantic import BaseModel


class PositionResponse(BaseModel):
  id: str
  market_id: str
  outcome_id: str
  outcome: str
  quantity: int
  locked_quantity: int
  average_entry_price_minor: int
  realized_pnl_minor: int
  status: str


class PositionPage(BaseModel):
  items: list[PositionResponse]
  next_cursor: str | None = None


class PortfolioResponse(BaseModel):
  positions: list[PositionResponse]
  total_quantity: int
  total_cost_minor: int
  max_payout_minor: int
