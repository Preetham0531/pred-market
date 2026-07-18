from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import AppError
from app.core.public_ids import public_id
from app.modules.positions.models import Position


def get_or_create_position(db: Session, *, user_id: str, market_id: str, outcome_id: str) -> Position:
  position = db.scalar(
    select(Position).where(
      Position.user_id == user_id,
      Position.market_id == market_id,
      Position.outcome_id == outcome_id,
    )
  )
  if position:
    return position
  position = Position(user_id=user_id, market_id=market_id, outcome_id=outcome_id)
  db.add(position)
  db.flush()
  return position


def add_position(db: Session, *, user_id: str, market_id: str, outcome_id: str, quantity: int, price_minor: int) -> Position:
  position = get_or_create_position(db, user_id=user_id, market_id=market_id, outcome_id=outcome_id)
  old_cost = position.quantity * position.average_entry_price_minor
  new_cost = quantity * price_minor
  position.quantity += quantity
  if position.quantity > 0:
    position.average_entry_price_minor = round((old_cost + new_cost) / position.quantity)
  return position


def lock_position_shares(db: Session, *, user_id: str, market_id: str, outcome_id: str, quantity: int) -> Position:
  position = get_or_create_position(db, user_id=user_id, market_id=market_id, outcome_id=outcome_id)
  if position.quantity - position.locked_quantity < quantity:
    raise AppError(422, "INSUFFICIENT_SHARES", "User does not have enough unlocked contracts to sell.")
  position.locked_quantity += quantity
  return position


def unlock_position_shares(db: Session, *, user_id: str, market_id: str, outcome_id: str, quantity: int) -> None:
  if quantity <= 0:
    return
  position = get_or_create_position(db, user_id=user_id, market_id=market_id, outcome_id=outcome_id)
  if position.locked_quantity < quantity:
    raise AppError(500, "POSITION_LOCK_UNDERFLOW", "Locked position would become negative.")
  position.locked_quantity -= quantity


def transfer_position(
  db: Session,
  *,
  seller_user_id: str,
  buyer_user_id: str,
  market_id: str,
  outcome_id: str,
  quantity: int,
  price_minor: int,
) -> None:
  seller = get_or_create_position(db, user_id=seller_user_id, market_id=market_id, outcome_id=outcome_id)
  if seller.locked_quantity < quantity or seller.quantity < quantity:
    raise AppError(500, "POSITION_UNDERFLOW", "Seller position would become negative.")
  seller.quantity -= quantity
  seller.locked_quantity -= quantity
  if seller.quantity == 0:
    seller.average_entry_price_minor = 0
  add_position(db, user_id=buyer_user_id, market_id=market_id, outcome_id=outcome_id, quantity=quantity, price_minor=price_minor)


def position_to_response(position: Position) -> dict:
  return {
    "id": public_id("POS", position.id),
    "market_id": position.market_id,
    "outcome_id": public_id("OUT", position.outcome_id),
    "outcome": position.outcome.label,
    "quantity": position.quantity,
    "locked_quantity": position.locked_quantity,
    "average_entry_price_minor": position.average_entry_price_minor,
    "realized_pnl_minor": position.realized_pnl_minor,
    "status": position.status,
  }


def list_user_positions(db: Session, *, user_id: str) -> list[Position]:
  return list(
    db.scalars(
      select(Position)
      .where(Position.user_id == user_id)
      .options(selectinload(Position.outcome), selectinload(Position.market))
      .order_by(Position.updated_at.desc())
    ).all()
  )
