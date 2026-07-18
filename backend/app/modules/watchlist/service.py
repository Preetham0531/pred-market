from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import AppError
from app.modules.markets.models import Market
from app.modules.markets.service import market_to_list_item
from app.modules.watchlist.models import WatchlistItem


def list_watchlist_markets(db: Session, *, user_id: str) -> list[dict]:
  rows = list(
    db.scalars(
      select(WatchlistItem)
      .where(WatchlistItem.user_id == user_id)
      .options(selectinload(WatchlistItem.market).selectinload(Market.outcomes))
      .order_by(WatchlistItem.created_at.desc())
    ).all()
  )
  return [market_to_list_item(row.market) for row in rows if row.market]


def add_watchlist_item(db: Session, *, user_id: str, market_id: str) -> WatchlistItem:
  market = db.get(Market, market_id)
  if not market:
    raise AppError(404, "MARKET_NOT_FOUND", "Market was not found.")
  existing = db.scalar(select(WatchlistItem).where(WatchlistItem.user_id == user_id, WatchlistItem.market_id == market_id))
  if existing:
    return existing
  item = WatchlistItem(user_id=user_id, market_id=market_id)
  db.add(item)
  db.flush()
  return item


def remove_watchlist_item(db: Session, *, user_id: str, market_id: str) -> bool:
  result = db.execute(delete(WatchlistItem).where(WatchlistItem.user_id == user_id, WatchlistItem.market_id == market_id))
  return bool(result.rowcount)
