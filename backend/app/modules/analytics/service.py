from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.public_ids import public_id
from app.core.security import utc_now
from app.modules.analytics.models import CategoryAnalytics, MarketAnalytics, UserAnalytics
from app.modules.markets.models import Category, Market, Outcome
from app.modules.orders.models import Order
from app.modules.positions.models import Position
from app.modules.trades.models import Trade
from app.modules.wallets.models import Wallet


def _upsert_market_analytics(db: Session, market: Market) -> MarketAnalytics:
  orders = list(db.scalars(select(Order).where(Order.market_id == market.id, Order.status.in_(["OPEN", "PARTIALLY_FILLED"]))).all())
  trades = list(db.scalars(select(Trade).where(Trade.market_id == market.id).order_by(Trade.created_at.desc())).all())
  positions = list(db.scalars(select(Position).where(Position.market_id == market.id, Position.quantity > 0)).all())

  active_buys = [order for order in orders if order.side == "BUY" and order.remaining_quantity > 0]
  best_bid = max((order.price_minor for order in active_buys), default=None)
  best_ask = min((100 - order.price_minor for order in active_buys), default=None)
  liquidity_depth = sum(order.remaining_quantity for order in orders)
  total_volume = sum(trade.price_minor * trade.quantity for trade in trades) or market.total_volume
  last_trade = trades[0].price_minor if trades else None
  spread = float(best_ask - best_bid) if best_bid is not None and best_ask is not None else market.spread
  open_interest = sum(position.quantity for position in positions)
  outcome_metrics = []
  for outcome in market.outcomes:
    outcome_orders = [order for order in orders if order.outcome_id == outcome.id]
    outcome_positions = [position for position in positions if position.outcome_id == outcome.id]
    outcome_metrics.append(
      {
        "outcome_id": public_id("OUT", outcome.id),
        "label": outcome.label,
        "price": outcome.price,
        "open_orders": len(outcome_orders),
        "open_quantity": sum(order.remaining_quantity for order in outcome_orders),
        "open_interest": sum(position.quantity for position in outcome_positions),
      }
    )

  row = db.scalar(select(MarketAnalytics).where(MarketAnalytics.market_id == market.id))
  if not row:
    row = MarketAnalytics(market_id=market.id)
    db.add(row)
  row.outcome_metrics_json = outcome_metrics
  row.best_bid = best_bid
  row.best_ask = best_ask
  row.last_trade = last_trade
  row.spread = spread
  row.volume_24h = market.volume_24h
  row.total_volume = total_volume
  row.open_interest = open_interest
  row.liquidity_depth = liquidity_depth
  row.price_change_24h = market.change_24h
  row.computed_at = utc_now()
  row.is_stale = False
  return row


def _upsert_category_analytics(db: Session, category: Category) -> CategoryAnalytics:
  markets = list(db.scalars(select(Market).where(Market.category_slug == category.slug)).all())
  active = [market for market in markets if market.status == "OPEN"]
  top_markets = sorted(markets, key=lambda item: item.volume_24h, reverse=True)[:5]
  top_movers = sorted(markets, key=lambda item: abs(item.change_24h), reverse=True)[:5]
  spreads = [market.spread for market in markets if market.spread is not None]
  row = db.scalar(select(CategoryAnalytics).where(CategoryAnalytics.category_slug == category.slug))
  if not row:
    row = CategoryAnalytics(category_slug=category.slug)
    db.add(row)
  row.active_markets = len(active)
  row.volume_24h = sum(market.volume_24h for market in markets)
  row.top_markets_json = [{"id": market.id, "title": market.title, "volume_24h": market.volume_24h} for market in top_markets]
  row.top_movers_json = [{"id": market.id, "title": market.title, "change_24h": market.change_24h} for market in top_movers]
  row.average_spread = sum(spreads) / len(spreads) if spreads else None
  row.liquidity_depth = sum(market.liquidity for market in markets)
  row.risk_alerts_json = [f"{category.risk} category controls apply."] if category.risk in {"HIGH", "RESTRICTED"} else []
  row.computed_at = utc_now()
  row.is_stale = False
  return row


def _upsert_user_analytics(db: Session, user_id: str) -> UserAnalytics:
  wallet = db.scalar(select(Wallet).where(Wallet.user_id == user_id))
  positions = list(db.scalars(select(Position).where(Position.user_id == user_id, Position.quantity > 0)).all())
  markets_by_id = {market.id: market for market in db.scalars(select(Market).where(Market.id.in_([p.market_id for p in positions] or [""]))).all()}
  outcomes_by_id = {outcome.id: outcome for outcome in db.scalars(select(Outcome).where(Outcome.id.in_([p.outcome_id for p in positions] or [""]))).all()}
  category_exposure: dict[str, int] = defaultdict(int)
  market_exposure: dict[str, int] = defaultdict(int)
  position_items = []
  max_payout = 0
  max_loss = 0
  realized_pnl = 0
  unrealized_pnl = 0
  for position in positions:
    market = markets_by_id.get(position.market_id)
    outcome = outcomes_by_id.get(position.outcome_id)
    cost = position.quantity * position.average_entry_price_minor
    payout = position.quantity * 100
    current_price = outcome.price if outcome else position.average_entry_price_minor
    current_value = position.quantity * current_price
    unrealized_pnl += current_value - cost
    realized_pnl += position.realized_pnl_minor
    max_payout += payout
    max_loss += cost
    if market:
      category_exposure[market.category_slug] += cost
      market_exposure[market.id] += cost
    position_items.append(
      {
        "market_id": position.market_id,
        "outcome_id": public_id("OUT", position.outcome_id),
        "outcome": outcome.label if outcome else None,
        "quantity": position.quantity,
        "average_entry_price_minor": position.average_entry_price_minor,
        "current_price_minor": current_price,
        "max_payout_minor": payout,
      }
    )
  row = db.scalar(select(UserAnalytics).where(UserAnalytics.user_id == user_id))
  if not row:
    row = UserAnalytics(user_id=user_id)
    db.add(row)
  row.available_cash = wallet.available_balance_minor if wallet else 0
  row.locked_cash = wallet.locked_balance_minor if wallet else 0
  row.positions_json = position_items
  row.category_exposure_json = [{"category_slug": key, "exposure_minor": value} for key, value in category_exposure.items()]
  row.market_exposure_json = [{"market_id": key, "exposure_minor": value} for key, value in market_exposure.items()]
  row.unrealized_pnl = unrealized_pnl
  row.realized_pnl = realized_pnl
  row.max_payout = max_payout
  row.max_loss = max_loss
  row.computed_at = utc_now()
  row.is_stale = False
  return row


def recompute_all(db: Session) -> dict[str, int]:
  markets = list(db.scalars(select(Market)).all())
  categories = list(db.scalars(select(Category)).all())
  user_ids = [row[0] for row in db.execute(select(Wallet.user_id).union(select(Position.user_id))).all()]
  for market in markets:
    _upsert_market_analytics(db, market)
  for category in categories:
    _upsert_category_analytics(db, category)
  for user_id in user_ids:
    _upsert_user_analytics(db, user_id)
  return {"markets": len(markets), "categories": len(categories), "users": len(user_ids)}


def get_market_analytics(db: Session, market_id: str) -> MarketAnalytics:
  market = db.get(Market, market_id)
  if not market:
    raise AppError(404, "MARKET_NOT_FOUND", "Market was not found.")
  return _upsert_market_analytics(db, market)


def get_category_analytics(db: Session, category_slug: str) -> CategoryAnalytics:
  category = db.get(Category, category_slug)
  if not category:
    raise AppError(404, "CATEGORY_NOT_FOUND", "Category was not found.")
  return _upsert_category_analytics(db, category)


def get_user_analytics(db: Session, user_id: str) -> UserAnalytics:
  return _upsert_user_analytics(db, user_id)


def market_analytics_to_response(row: MarketAnalytics) -> dict:
  return {
    "market_id": row.market_id,
    "outcome_metrics": row.outcome_metrics_json,
    "best_bid": row.best_bid,
    "best_ask": row.best_ask,
    "last_trade": row.last_trade,
    "spread": row.spread,
    "volume_24h": row.volume_24h,
    "total_volume": row.total_volume,
    "open_interest": row.open_interest,
    "liquidity_depth": row.liquidity_depth,
    "price_change_24h": row.price_change_24h,
    "computed_at": row.computed_at,
    "is_stale": row.is_stale,
  }


def category_analytics_to_response(row: CategoryAnalytics) -> dict:
  return {
    "category_slug": row.category_slug,
    "active_markets": row.active_markets,
    "volume_24h": row.volume_24h,
    "top_markets": row.top_markets_json,
    "top_movers": row.top_movers_json,
    "average_spread": row.average_spread,
    "liquidity_depth": row.liquidity_depth,
    "risk_alerts": row.risk_alerts_json,
    "computed_at": row.computed_at,
    "is_stale": row.is_stale,
  }


def user_analytics_to_response(row: UserAnalytics) -> dict:
  return {
    "user_id": public_id("USR", row.user_id),
    "available_cash": row.available_cash,
    "locked_cash": row.locked_cash,
    "positions": row.positions_json,
    "category_exposure": row.category_exposure_json,
    "market_exposure": row.market_exposure_json,
    "unrealized_pnl": row.unrealized_pnl,
    "realized_pnl": row.realized_pnl,
    "max_payout": row.max_payout,
    "max_loss": row.max_loss,
    "computed_at": row.computed_at,
    "is_stale": row.is_stale,
  }
