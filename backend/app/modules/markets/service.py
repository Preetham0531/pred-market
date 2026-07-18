from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import AppError
from app.core.public_ids import public_id
from app.modules.markets.models import Category, Market
from app.modules.orders.models import Order
from app.modules.trades.models import Trade


def category_to_response(category: Category) -> dict:
  return {
    "slug": category.slug,
    "name": category.name,
    "short_name": category.short_name,
    "description": category.description,
    "active_markets": category.active_markets,
    "volume_24h": category.volume_24h,
    "total_volume": category.total_volume,
    "risk": category.risk,
    "icon_tone": category.icon_tone,
    "focus": category.focus_json,
  }


def market_to_list_item(market: Market) -> dict:
  return {
    "id": market.id,
    "title": market.title,
    "category_slug": market.category_slug,
    "subcategory": market.subcategory,
    "market_type": market.market_type,
    "status": market.status,
    "close_time": market.close_time,
    "source": market.source,
    "rule_summary": market.rule_summary,
    "probability": market.probability,
    "change_24h": market.change_24h,
    "volume_24h": market.volume_24h,
    "total_volume": market.total_volume,
    "liquidity": market.liquidity,
    "spread": market.spread,
    "traders": market.traders,
    "outcomes": [
      {"id": public_id("OUT", outcome.id), "label": outcome.label, "price": outcome.price, "probability": outcome.probability}
      for outcome in market.outcomes
    ],
    "risk_notes": market.risk_notes_json,
  }


def market_to_detail(market: Market) -> dict:
  return {
    **market_to_list_item(market),
    "price_history": market.price_history_json,
    "order_book": market.order_book_json,
    "recent_trades": market.recent_trades_json,
  }


def computed_order_book(db: Session, market: Market) -> dict:
  orders = list(
    db.scalars(
      select(Order)
      .where(Order.market_id == market.id, Order.side == "BUY", Order.status.in_(["OPEN", "PARTIALLY_FILLED"]))
      .options(selectinload(Order.outcome))
    ).all()
  )
  if not orders:
    return market.order_book_json
  yes_levels: dict[int, int] = {}
  no_levels: dict[int, int] = {}
  for order in orders:
    if order.remaining_quantity <= 0:
      continue
    if order.outcome.label == "YES":
      yes_levels[order.price_minor] = yes_levels.get(order.price_minor, 0) + order.remaining_quantity
    elif order.outcome.label == "NO":
      no_levels[order.price_minor] = no_levels.get(order.price_minor, 0) + order.remaining_quantity
  return {
    "yes_bids": [{"price": price, "quantity": quantity} for price, quantity in sorted(yes_levels.items(), reverse=True)],
    "no_bids": [{"price": price, "quantity": quantity} for price, quantity in sorted(no_levels.items(), reverse=True)],
  }


def computed_recent_trades(db: Session, market: Market) -> list[dict]:
  trades = list(
    db.scalars(
      select(Trade)
      .where(Trade.market_id == market.id)
      .options(selectinload(Trade.outcome))
      .order_by(Trade.created_at.desc())
      .limit(25)
    ).all()
  )
  if not trades:
    return market.recent_trades_json
  return [
    {
      "time": trade.created_at.isoformat(),
      "outcome": trade.outcome.label,
      "price": trade.price_minor,
      "quantity": trade.quantity,
    }
    for trade in trades
  ]


def list_markets(db: Session, *, category: str | None, status: str | None, q: str | None, limit: int) -> list[Market]:
  stmt = select(Market).options(selectinload(Market.outcomes)).order_by(Market.volume_24h.desc())
  if category:
    stmt = stmt.where(Market.category_slug == category)
  if status:
    stmt = stmt.where(Market.status == status)
  if q:
    stmt = stmt.where(Market.title.ilike(f"%{q}%"))
  return list(db.scalars(stmt.limit(limit)).all())


def list_categories(db: Session) -> list[Category]:
  return list(db.scalars(select(Category).order_by(Category.name.asc())).all())


def get_market_or_404(db: Session, market_id: str) -> Market:
  market = db.scalar(select(Market).where(Market.id == market_id).options(selectinload(Market.outcomes)))
  if not market:
    raise AppError(404, "MARKET_NOT_FOUND", "Market was not found.")
  return market


def get_category_or_404(db: Session, category_slug: str) -> Category:
  category = db.get(Category, category_slug)
  if not category:
    raise AppError(404, "CATEGORY_NOT_FOUND", "Category was not found.")
  return category
