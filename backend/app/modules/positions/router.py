from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.positions.schemas import PortfolioResponse, PositionPage
from app.modules.positions.service import list_user_positions, position_to_response
from app.modules.users.models import User

router = APIRouter()


@router.get("/positions", response_model=PositionPage)
def list_positions_endpoint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
  return {"items": [position_to_response(position) for position in list_user_positions(db, user_id=user.id)], "next_cursor": None}


@router.get("/portfolio", response_model=PortfolioResponse)
def portfolio_endpoint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
  positions = list_user_positions(db, user_id=user.id)
  items = [position_to_response(position) for position in positions]
  total_cost = sum(position.quantity * position.average_entry_price_minor for position in positions)
  max_payout = sum(position.quantity * 100 for position in positions)
  return {
    "positions": items,
    "total_quantity": sum(position.quantity for position in positions),
    "total_cost_minor": total_cost,
    "max_payout_minor": max_payout,
  }
