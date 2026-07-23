from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import AppError
from app.core.public_ids import matches_public_id, public_id
from app.core.security import utc_now
from app.modules.audit.service import write_audit_log
from app.modules.markets.models import Market, Outcome
from app.modules.markets.service import update_market_after_trade
from app.modules.orders.models import Order
from app.modules.positions.service import add_position, lock_position_shares, transfer_position, unlock_position_shares
from app.modules.realtime.service import write_market_event, write_user_event
from app.modules.trades.models import Trade
from app.modules.users.models import User
from app.modules.wallets.service import (
  lock_cash_for_order,
  move_locked_cash_to_market_collateral,
  release_locked_cash,
  transfer_locked_cash_to_user_available,
)

BINARY_TYPES = {"Binary", "Threshold", "Conditional", "Combo"}


def order_to_response(order: Order) -> dict:
  return {
    "id": public_id("ORD", order.id),
    "user_id": public_id("USR", order.user_id),
    "market_id": order.market_id,
    "outcome_id": public_id("OUT", order.outcome_id),
    "outcome": order.outcome.label,
    "side": order.side,
    "price_minor": order.price_minor,
    "quantity": order.quantity,
    "filled_quantity": order.filled_quantity,
    "cancelled_quantity": order.cancelled_quantity,
    "remaining_quantity": order.remaining_quantity,
    "locked_cash_minor": order.locked_cash_minor,
    "locked_shares": order.locked_shares,
    "status": order.status,
    "created_at": order.created_at,
    "updated_at": order.updated_at,
    "cancelled_at": order.cancelled_at,
  }


def resolve_outcome(db: Session, *, market_id: str, outcome_id: str | None, outcome_label: str | None) -> Outcome:
  if outcome_id:
    outcome = db.get(Outcome, outcome_id)
    if outcome and outcome.market_id == market_id:
      return outcome
    outcomes = db.scalars(select(Outcome).where(Outcome.market_id == market_id)).all()
    for candidate in outcomes:
      if matches_public_id("OUT", candidate.id, outcome_id):
        return candidate
  if outcome_label:
    outcome = db.scalar(select(Outcome).where(Outcome.market_id == market_id, Outcome.label == outcome_label))
    if outcome:
      return outcome
  raise AppError(404, "OUTCOME_NOT_FOUND", "Outcome was not found for this market.")


def validate_market_for_order(market: Market) -> None:
  if market.status != "OPEN":
    raise AppError(422, "MARKET_NOT_OPEN", "Market is not open for trading.")


def update_order_status(order: Order) -> None:
  if order.filled_quantity == order.quantity:
    order.status = "FILLED"
  elif order.cancelled_quantity and order.remaining_quantity == 0:
    order.status = "PARTIALLY_CANCELLED" if order.filled_quantity else "CANCELLED"
  elif order.filled_quantity:
    order.status = "PARTIALLY_FILLED"
  else:
    order.status = "OPEN"


def compatible_binary_outcome(db: Session, outcome: Outcome) -> Outcome:
  if outcome.label == "YES":
    label = "NO"
  elif outcome.label == "NO":
    label = "YES"
  else:
    raise AppError(422, "UNSUPPORTED_BINARY_OUTCOME", "Binary complementary matching requires YES/NO outcomes.")
  other = db.scalar(select(Outcome).where(Outcome.market_id == outcome.market_id, Outcome.label == label))
  if not other:
    raise AppError(422, "COMPLEMENT_OUTCOME_MISSING", "Complementary outcome is missing.")
  return other


def create_order(
  db: Session,
  *,
  payload,
  user: User,
  idempotency_key: str,
  request_id: str | None,
) -> Order:
  if not idempotency_key:
    raise AppError(400, "IDEMPOTENCY_KEY_REQUIRED", "Idempotency-Key header is required.")
  existing = db.scalar(
    select(Order)
    .where(Order.idempotency_key == idempotency_key)
    .options(selectinload(Order.outcome))
  )
  if existing:
    return existing

  market = db.get(Market, payload.market_id)
  if not market:
    raise AppError(404, "MARKET_NOT_FOUND", "Market was not found.")
  validate_market_for_order(market)
  outcome = resolve_outcome(db, market_id=market.id, outcome_id=payload.outcome_id, outcome_label=payload.outcome)

  order = Order(
    user_id=user.id,
    market_id=market.id,
    outcome_id=outcome.id,
    side=payload.side,
    price_minor=payload.price_minor,
    quantity=payload.quantity,
    status="OPEN",
    idempotency_key=idempotency_key,
  )
  db.add(order)
  db.flush()

  if order.side == "BUY":
    locked_amount = order.price_minor * order.quantity
    lock_cash_for_order(db, user_id=user.id, amount_minor=locked_amount, order_id=order.id, idempotency_key=f"ORDER_LOCK:{order.id}")
    order.locked_cash_minor = locked_amount
  else:
    lock_position_shares(db, user_id=user.id, market_id=market.id, outcome_id=outcome.id, quantity=order.quantity)
    order.locked_shares = order.quantity

  if market.market_type in BINARY_TYPES:
    match_binary_order(db, order, outcome)
  else:
    match_outcome_order_book(db, order)

  update_order_status(order)
  write_audit_log(
    db,
    event_type="ORDER_CREATED",
    actor_user_id=user.id,
    request_id=request_id,
    metadata={"order_id": order.id, "status": order.status},
  )
  write_market_event(
    db,
    event_type="order_book.delta",
    market_id=order.market_id,
    suffix="order_book",
    payload={"order_id": order.id, "status": order.status, "side": order.side, "outcome_id": order.outcome_id},
  )
  write_user_event(
    db,
    event_type="order.updated",
    user_id=user.id,
    suffix="orders",
    market_id=order.market_id,
    payload=order_to_response(order),
  )
  return order


def match_binary_order(db: Session, incoming: Order, outcome: Outcome) -> None:
  if incoming.side != "BUY":
    return
  complement = compatible_binary_outcome(db, outcome)
  required_price = 100 - incoming.price_minor
  resting_orders = list(
    db.scalars(
      select(Order)
      .where(
        Order.market_id == incoming.market_id,
        Order.outcome_id == complement.id,
        Order.side == "BUY",
        Order.price_minor >= required_price,
        Order.status.in_(["OPEN", "PARTIALLY_FILLED"]),
        Order.user_id != incoming.user_id,
      )
      .order_by(Order.price_minor.desc(), Order.created_at.asc(), Order.id.asc())
      .options(selectinload(Order.outcome))
    ).all()
  )
  for resting in resting_orders:
    if incoming.remaining_quantity <= 0:
      break
    quantity = min(incoming.remaining_quantity, resting.remaining_quantity)
    execute_binary_fill(db, incoming=incoming, resting=resting, quantity=quantity, incoming_outcome=outcome, resting_outcome=complement)


def execute_binary_fill(db: Session, *, incoming: Order, resting: Order, quantity: int, incoming_outcome: Outcome, resting_outcome: Outcome) -> None:
  incoming_fill_price = 100 - resting.price_minor
  incoming_amount = incoming_fill_price * quantity
  resting_amount = resting.price_minor * quantity
  incoming.filled_quantity += quantity
  resting.filled_quantity += quantity
  incoming.locked_cash_minor -= incoming_amount
  resting.locked_cash_minor -= resting_amount
  price_improvement = (incoming.price_minor - incoming_fill_price) * quantity
  if price_improvement > 0:
    release_locked_cash(
      db,
      user_id=incoming.user_id,
      amount_minor=price_improvement,
      reference_id=f"{incoming.id}:{resting.id}:{incoming.filled_quantity}",
    )
    incoming.locked_cash_minor -= price_improvement
  trade = Trade(
    market_id=incoming.market_id,
    outcome_id=incoming.outcome_id,
    price_minor=incoming_fill_price,
    quantity=quantity,
    buyer_user_id=incoming.user_id,
    seller_user_id=resting.user_id,
    yes_order_id=incoming.id if incoming_outcome.label == "YES" else resting.id,
    no_order_id=incoming.id if incoming_outcome.label == "NO" else resting.id,
  )
  db.add(trade)
  db.flush()
  move_locked_cash_to_market_collateral(db, user_id=incoming.user_id, market_id=incoming.market_id, amount_minor=incoming_amount, reference_id=trade.id)
  move_locked_cash_to_market_collateral(db, user_id=resting.user_id, market_id=resting.market_id, amount_minor=resting_amount, reference_id=trade.id)
  add_position(db, user_id=incoming.user_id, market_id=incoming.market_id, outcome_id=incoming.outcome_id, quantity=quantity, price_minor=incoming_fill_price)
  add_position(db, user_id=resting.user_id, market_id=resting.market_id, outcome_id=resting.outcome_id, quantity=quantity, price_minor=resting.price_minor)
  update_order_status(resting)
  update_market_after_trade(
    db,
    incoming.market,
    incoming_outcome,
    price_minor=incoming_fill_price,
    quantity=quantity,
    traded_at=trade.created_at or utc_now(),
  )
  write_market_event(db, event_type="trade.created", market_id=incoming.market_id, suffix="trades", payload={"trade_id": trade.id, "price_minor": trade.price_minor, "quantity": trade.quantity})
  write_market_event(
    db,
    event_type="ticker.updated",
    market_id=incoming.market_id,
    suffix="ticker",
    payload={"probability": incoming.market.probability, "volume_24h": incoming.market.volume_24h, "spread": incoming.market.spread},
  )
  write_user_event(db, event_type="position.updated", user_id=incoming.user_id, suffix="positions", market_id=incoming.market_id, payload={"market_id": incoming.market_id, "outcome_id": incoming.outcome_id})
  write_user_event(db, event_type="position.updated", user_id=resting.user_id, suffix="positions", market_id=resting.market_id, payload={"market_id": resting.market_id, "outcome_id": resting.outcome_id})


def match_outcome_order_book(db: Session, incoming: Order) -> None:
  if incoming.side == "BUY":
    resting_orders = list(
      db.scalars(
        select(Order)
        .where(
          Order.market_id == incoming.market_id,
          Order.outcome_id == incoming.outcome_id,
          Order.side == "SELL",
          Order.price_minor <= incoming.price_minor,
          Order.status.in_(["OPEN", "PARTIALLY_FILLED"]),
          Order.user_id != incoming.user_id,
        )
        .order_by(Order.price_minor.asc(), Order.created_at.asc(), Order.id.asc())
        .options(selectinload(Order.outcome))
      ).all()
    )
  else:
    resting_orders = list(
      db.scalars(
        select(Order)
        .where(
          Order.market_id == incoming.market_id,
          Order.outcome_id == incoming.outcome_id,
          Order.side == "BUY",
          Order.price_minor >= incoming.price_minor,
          Order.status.in_(["OPEN", "PARTIALLY_FILLED"]),
          Order.user_id != incoming.user_id,
        )
        .order_by(Order.price_minor.desc(), Order.created_at.asc(), Order.id.asc())
        .options(selectinload(Order.outcome))
      ).all()
    )
  for resting in resting_orders:
    if incoming.remaining_quantity <= 0:
      break
    quantity = min(incoming.remaining_quantity, resting.remaining_quantity)
    execute_outcome_fill(db, incoming=incoming, resting=resting, quantity=quantity)


def execute_outcome_fill(db: Session, *, incoming: Order, resting: Order, quantity: int) -> None:
  fill_price = resting.price_minor
  if incoming.side == "BUY":
    buy_order, sell_order = incoming, resting
  else:
    buy_order, sell_order = resting, incoming
  buyer_id = buy_order.user_id
  seller_id = sell_order.user_id
  cash_to_seller = fill_price * quantity
  buy_order.filled_quantity += quantity
  sell_order.filled_quantity += quantity
  buy_order.locked_cash_minor -= cash_to_seller
  sell_order.locked_shares -= quantity
  if incoming.side == "BUY" and incoming.price_minor > fill_price:
    release_locked_cash(
      db,
      user_id=incoming.user_id,
      amount_minor=(incoming.price_minor - fill_price) * quantity,
      reference_id=f"{incoming.id}:{resting.id}:{incoming.filled_quantity}",
    )
    incoming.locked_cash_minor -= (incoming.price_minor - fill_price) * quantity
  trade = Trade(
    market_id=incoming.market_id,
    outcome_id=incoming.outcome_id,
    price_minor=fill_price,
    quantity=quantity,
    buyer_user_id=buyer_id,
    seller_user_id=seller_id,
    buy_order_id=buy_order.id,
    sell_order_id=sell_order.id,
  )
  db.add(trade)
  db.flush()
  transfer_locked_cash_to_user_available(db, from_user_id=buyer_id, to_user_id=seller_id, amount_minor=cash_to_seller, reference_id=trade.id)
  transfer_position(db, seller_user_id=seller_id, buyer_user_id=buyer_id, market_id=incoming.market_id, outcome_id=incoming.outcome_id, quantity=quantity, price_minor=fill_price)
  update_order_status(resting)
  update_market_after_trade(
    db,
    incoming.market,
    incoming.outcome,
    price_minor=fill_price,
    quantity=quantity,
    traded_at=trade.created_at or utc_now(),
  )
  write_market_event(db, event_type="trade.created", market_id=incoming.market_id, suffix="trades", payload={"trade_id": trade.id, "price_minor": trade.price_minor, "quantity": trade.quantity})
  write_market_event(
    db,
    event_type="ticker.updated",
    market_id=incoming.market_id,
    suffix="ticker",
    payload={"probability": incoming.market.probability, "volume_24h": incoming.market.volume_24h, "spread": incoming.market.spread},
  )
  write_user_event(db, event_type="position.updated", user_id=buyer_id, suffix="positions", market_id=incoming.market_id, payload={"market_id": incoming.market_id, "outcome_id": incoming.outcome_id})
  write_user_event(db, event_type="position.updated", user_id=seller_id, suffix="positions", market_id=incoming.market_id, payload={"market_id": incoming.market_id, "outcome_id": incoming.outcome_id})


def cancel_order(db: Session, *, order_id: str, user: User, request_id: str | None) -> Order:
  order = resolve_order_by_public_or_internal_id(db, order_id)
  if not order:
    raise AppError(404, "ORDER_NOT_FOUND", "Order was not found.")
  roles = {role.role for role in user.roles}
  if order.user_id != user.id and "ADMIN" not in roles:
    raise AppError(403, "FORBIDDEN", "You do not have permission to cancel this order.")
  if order.status not in {"OPEN", "PARTIALLY_FILLED"}:
    return order
  remaining = order.remaining_quantity
  order.cancelled_quantity += remaining
  order.cancelled_at = utc_now()
  if order.side == "BUY":
    release_amount = order.locked_cash_minor
    release_locked_cash(db, user_id=order.user_id, amount_minor=release_amount, reference_id=order.id)
    order.locked_cash_minor = 0
  else:
    unlock_position_shares(db, user_id=order.user_id, market_id=order.market_id, outcome_id=order.outcome_id, quantity=order.locked_shares)
    order.locked_shares = 0
  update_order_status(order)
  write_audit_log(
    db,
    event_type="ORDER_CANCELLED",
    actor_user_id=user.id,
    target_user_id=order.user_id,
    request_id=request_id,
    metadata={"order_id": order.id},
  )
  write_market_event(db, event_type="order_book.delta", market_id=order.market_id, suffix="order_book", payload={"order_id": order.id, "status": order.status})
  write_user_event(db, event_type="order.updated", user_id=order.user_id, suffix="orders", market_id=order.market_id, payload=order_to_response(order))
  return order


def cancel_market_open_orders(db: Session, *, market_id: str) -> list[Order]:
  orders = list(
    db.scalars(
      select(Order)
      .where(Order.market_id == market_id, Order.status.in_(["OPEN", "PARTIALLY_FILLED"]))
      .options(selectinload(Order.outcome))
    ).all()
  )
  for order in orders:
    if order.side == "BUY" and order.locked_cash_minor > 0:
      release_locked_cash(db, user_id=order.user_id, amount_minor=order.locked_cash_minor, reference_id=order.id)
      order.locked_cash_minor = 0
    if order.side == "SELL" and order.locked_shares > 0:
      unlock_position_shares(db, user_id=order.user_id, market_id=order.market_id, outcome_id=order.outcome_id, quantity=order.locked_shares)
    order.cancelled_quantity += order.remaining_quantity
    order.locked_shares = 0
    order.cancelled_at = utc_now()
    update_order_status(order)
  return orders


def get_order_or_404(db: Session, *, order_id: str, user: User) -> Order:
  order = resolve_order_by_public_or_internal_id(db, order_id)
  if not order:
    raise AppError(404, "ORDER_NOT_FOUND", "Order was not found.")
  roles = {role.role for role in user.roles}
  if order.user_id != user.id and "ADMIN" not in roles:
    raise AppError(403, "FORBIDDEN", "You do not have permission to view this order.")
  return order


def resolve_order_by_public_or_internal_id(db: Session, order_id: str) -> Order | None:
  order = db.scalar(select(Order).where(Order.id == order_id).options(selectinload(Order.outcome)))
  if order:
    return order
  orders = db.scalars(select(Order).options(selectinload(Order.outcome))).all()
  for candidate in orders:
    if matches_public_id("ORD", candidate.id, order_id):
      return candidate
  return None


def list_user_orders(db: Session, *, user_id: str) -> list[Order]:
  return list(
    db.scalars(
      select(Order)
      .where(Order.user_id == user_id)
      .options(selectinload(Order.outcome))
      .order_by(Order.created_at.desc())
    ).all()
  )
