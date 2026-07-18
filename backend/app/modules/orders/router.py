from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.core.rate_limit import check_rate_limit
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user, get_current_user_for_write
from app.modules.orders.schemas import OrderCreate, OrderPage, OrderResponse
from app.modules.orders.service import cancel_order, create_order, get_order_or_404, list_user_orders, order_to_response
from app.modules.realtime.service import publish_pending_events
from app.modules.users.models import User

router = APIRouter()


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order_endpoint(
  payload: OrderCreate,
  request: Request,
  idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
  user: User = Depends(get_current_user_for_write),
  db: Session = Depends(get_db),
):
  check_rate_limit(key=f"orders:create:user:{user.id}", limit=60, window_seconds=60)
  order = create_order(db, payload=payload, user=user, idempotency_key=idempotency_key or "", request_id=getattr(request.state, "request_id", None))
  db.commit()
  await publish_pending_events(db)
  db.commit()
  return order_to_response(order)


@router.get("", response_model=OrderPage)
def list_orders_endpoint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
  return {"items": [order_to_response(order) for order in list_user_orders(db, user_id=user.id)], "next_cursor": None}


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_endpoint(order_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
  return order_to_response(get_order_or_404(db, order_id=order_id, user=user))


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order_endpoint(order_id: str, request: Request, user: User = Depends(get_current_user_for_write), db: Session = Depends(get_db)):
  check_rate_limit(key=f"orders:cancel:user:{user.id}", limit=90, window_seconds=60)
  order = cancel_order(db, order_id=order_id, user=user, request_id=getattr(request.state, "request_id", None))
  db.commit()
  await publish_pending_events(db)
  db.commit()
  return order_to_response(order)
