from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import AppError
from app.core.public_ids import public_id
from app.modules.markets.models import Category, Market, Outcome
from app.modules.orders.models import Order
from app.modules.realtime.models import RealtimeEvent
from app.modules.trades.models import Trade
from app.modules.users.models import User


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


def market_to_list_item(db: Session, market: Market) -> dict:
  book = computed_order_book(db, market)
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
    "quote": computed_quote(db, market, book=book),
  }


def market_to_detail(db: Session, market: Market) -> dict:
  return {
    **market_to_list_item(db, market),
    "price_history": market.price_history_json,
    "order_book": computed_order_book(db, market),
    "recent_trades": computed_recent_trades(db, market),
  }


def computed_order_book(db: Session, market: Market) -> dict:
  orders = list(
    db.scalars(
      select(Order)
      .where(Order.market_id == market.id, Order.side == "BUY", Order.status.in_(["OPEN", "PARTIALLY_FILLED"]))
      .options(selectinload(Order.outcome))
    ).all()
  )
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


def computed_quote(db: Session, market: Market, *, book: dict | None = None) -> dict:
  order_book = book or computed_order_book(db, market)
  yes_bids = order_book.get("yes_bids") or []
  no_bids = order_book.get("no_bids") or []
  yes_bid = yes_bids[0]["price"] if yes_bids else None
  no_bid = no_bids[0]["price"] if no_bids else None
  last_trade = db.scalar(
    select(Trade.price_minor)
    .where(Trade.market_id == market.id)
    .order_by(Trade.created_at.desc(), Trade.id.desc())
    .limit(1)
  )
  yes_ask = 100 - no_bid if no_bid is not None else None
  no_ask = 100 - yes_bid if yes_bid is not None else None
  spread = max(0, yes_ask - yes_bid) if yes_ask is not None and yes_bid is not None else None
  return {
    "yes_bid": yes_bid,
    "yes_ask": yes_ask,
    "no_bid": no_bid,
    "no_ask": no_ask,
    "last_trade": last_trade,
    "spread": spread,
  }


def order_book_snapshot(db: Session, market: Market) -> dict:
  book = computed_order_book(db, market)
  latest_event = db.scalar(
    select(RealtimeEvent)
    .where(
      RealtimeEvent.market_id == market.id,
      RealtimeEvent.event_type.in_(["order_book.snapshot", "order_book.delta"]),
    )
    .order_by(RealtimeEvent.sequence.desc())
    .limit(1)
  )
  return {
    "market_id": market.id,
    "sequence": int(latest_event.sequence if latest_event else 0),
    "updated_at": (
      latest_event.created_at.isoformat()
      if latest_event and latest_event.created_at
      else market.updated_at.isoformat()
      if market.updated_at
      else ""
    ),
    "quote": computed_quote(db, market, book=book),
    "order_book": book,
  }


def write_order_book_snapshot_event(db: Session, market: Market) -> None:
  from app.modules.realtime.service import write_market_event

  snapshot = order_book_snapshot(db, market)
  write_market_event(
    db,
    event_type="order_book.snapshot",
    market_id=market.id,
    suffix="order_book",
    payload={
      "updated_at": snapshot["updated_at"],
      "quote": snapshot["quote"],
      "order_book": snapshot["order_book"],
    },
  )


def update_market_after_trade(db: Session, market: Market, outcome: Outcome, *, price_minor: int, quantity: int, traded_at) -> None:
  yes_price = price_minor if outcome.label == "YES" else 100 - price_minor if outcome.label == "NO" else market.probability
  previous = market.probability
  market.probability = yes_price
  market.change_24h = float(yes_price - previous)
  market.volume_24h += price_minor * quantity
  market.total_volume += price_minor * quantity
  trader_ids: set[str] = set()
  for buyer_id, seller_id in db.execute(
    select(Trade.buyer_user_id, Trade.seller_user_id).where(Trade.market_id == market.id)
  ).all():
    trader_ids.add(buyer_id)
    if seller_id:
      trader_ids.add(seller_id)
  if trader_ids:
    market.traders = len(
      db.scalars(select(User.id).where(User.id.in_(trader_ids), User.is_system.is_(False))).all()
    )
  history = list(market.price_history_json or [])
  history.append({"time": traded_at.isoformat(), "value": yes_price, "volume": price_minor * quantity})
  market.price_history_json = history[-240:]
  for candidate in market.outcomes:
    if candidate.label == "YES":
      candidate.price = yes_price
      candidate.probability = yes_price
    elif candidate.label == "NO":
      candidate.price = 100 - yes_price
      candidate.probability = 100 - yes_price
  db.flush()
  book = computed_order_book(db, market)
  quote = computed_quote(db, market, book=book)
  market.spread = float(quote["spread"] or 0)
  market.liquidity = sum(level["price"] * level["quantity"] for side in book.values() for level in side)


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
