from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.security import hash_password, new_token, utc_now
from app.modules.markets.models import Market, Outcome
from app.modules.orders.models import Order
from app.modules.orders.service import BINARY_TYPES, cancel_order, create_order
from app.modules.users.models import User
from app.modules.wallets.service import get_or_create_wallet, test_deposit

SYSTEM_MAKER_EMAIL = "liquidity@system.pred-market.invalid"


def get_or_create_market_maker(db: Session) -> User:
  maker = db.scalar(select(User).where(User.is_system.is_(True), User.email == SYSTEM_MAKER_EMAIL))
  if maker:
    return maker
  maker = User(
    email=SYSTEM_MAKER_EMAIL,
    password_hash=hash_password(new_token(48)),
    display_name="System liquidity",
    status="ACTIVE",
    email_verified_at=utc_now(),
    is_system=True,
  )
  db.add(maker)
  db.flush()
  return maker


def fund_market_maker(db: Session, maker: User) -> None:
  get_or_create_wallet(db, maker.id)
  test_deposit(
    db,
    user=maker,
    amount_minor=settings.simulated_market_maker_cash_minor,
    currency="INR",
    idempotency_key=f"MARKET_MAKER_FUND:{maker.id}",
    request_id=None,
  )


def target_levels(market: Market) -> dict[str, list[tuple[int, int]]]:
  depth = settings.simulated_market_maker_depth_levels
  midpoint = max(6, min(94, int(market.probability)))
  yes_best = midpoint - 1
  no_best = 100 - (midpoint + 1)
  return {
    "YES": [(yes_best - index, quantity) for index, quantity in enumerate(depth)],
    "NO": [(no_best - index, quantity) for index, quantity in enumerate(depth)],
  }


def replenish_market_liquidity(db: Session, market_id: str, *, force: bool = False) -> int:
  if not force and not settings.simulated_market_maker_active:
    return 0
  market = db.scalar(
    select(Market)
    .where(Market.id == market_id)
    .with_for_update()
    .options(selectinload(Market.outcomes))
  )
  if not market or market.status != "OPEN" or market.market_type not in BINARY_TYPES:
    return 0
  outcomes = {outcome.label: outcome for outcome in market.outcomes}
  if "YES" not in outcomes or "NO" not in outcomes:
    return 0

  maker = get_or_create_market_maker(db)
  fund_market_maker(db, maker)
  desired_prices = {label: {price for price, _ in levels} for label, levels in target_levels(market).items()}
  stale_orders = list(
    db.scalars(
      select(Order)
      .where(
        Order.user_id == maker.id,
        Order.market_id == market.id,
        Order.status.in_(["OPEN", "PARTIALLY_FILLED"]),
      )
      .options(selectinload(Order.outcome))
    ).all()
  )
  for stale in stale_orders:
    if stale.price_minor not in desired_prices.get(stale.outcome.label, set()):
      cancel_order(db, order_id=stale.id, user=maker, request_id=None)

  created = 0
  for label, levels in target_levels(market).items():
    outcome = outcomes[label]
    for price, target_quantity in levels:
      if not 1 <= price <= 99:
        continue
      existing_quantity = sum(
        order.remaining_quantity
        for order in db.scalars(
          select(Order).where(
            Order.user_id == maker.id,
            Order.market_id == market.id,
            Order.outcome_id == outcome.id,
            Order.side == "BUY",
            Order.price_minor == price,
            Order.status.in_(["OPEN", "PARTIALLY_FILLED"]),
          )
        ).all()
      )
      missing = target_quantity - existing_quantity
      if missing <= 0:
        continue
      create_order(
        db,
        payload=SimpleNamespace(
          market_id=market.id,
          outcome_id=outcome.id,
          outcome=None,
          side="BUY",
          price_minor=price,
          quantity=missing,
        ),
        user=maker,
        idempotency_key=f"MARKET_MAKER:{market.id}:{label}:{price}:{uuid4().hex}",
        request_id=None,
      )
      created += 1
  return created


def replenish_all_open_markets(db: Session, *, force: bool = False) -> int:
  market_ids = list(
    db.scalars(
      select(Market.id).where(Market.status == "OPEN", Market.market_type.in_(BINARY_TYPES)).order_by(Market.id)
    ).all()
  )
  return sum(replenish_market_liquidity(db, market_id, force=force) for market_id in market_ids)
