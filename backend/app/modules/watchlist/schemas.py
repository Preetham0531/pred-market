from pydantic import BaseModel

from app.modules.markets.schemas import MarketListItem


class WatchlistPage(BaseModel):
  items: list[MarketListItem]
  next_cursor: str | None = None


class WatchlistActionResponse(BaseModel):
  market_id: str
  watchlisted: bool
