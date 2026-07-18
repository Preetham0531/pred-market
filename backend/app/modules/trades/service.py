from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.public_ids import public_id
from app.modules.trades.models import Trade


def trade_to_response(trade: Trade) -> dict:
  return {
    "id": public_id("TRD", trade.id),
    "market_id": trade.market_id,
    "outcome_id": public_id("OUT", trade.outcome_id),
    "outcome": trade.outcome.label,
    "price_minor": trade.price_minor,
    "quantity": trade.quantity,
    "buyer_user_id": public_id("USR", trade.buyer_user_id),
    "seller_user_id": public_id("USR", trade.seller_user_id),
    "status": trade.status,
    "created_at": trade.created_at,
  }


def list_user_trades(db: Session, *, user_id: str) -> list[Trade]:
  return list(
    db.scalars(
      select(Trade)
      .where(or_(Trade.buyer_user_id == user_id, Trade.seller_user_id == user_id))
      .options(selectinload(Trade.outcome))
      .order_by(Trade.created_at.desc())
    ).all()
  )
