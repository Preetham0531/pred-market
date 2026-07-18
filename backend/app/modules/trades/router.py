from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.trades.schemas import TradePage
from app.modules.trades.service import list_user_trades, trade_to_response
from app.modules.users.models import User

router = APIRouter()


@router.get("", response_model=TradePage)
def list_trades_endpoint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
  return {"items": [trade_to_response(trade) for trade in list_user_trades(db, user_id=user.id)], "next_cursor": None}
