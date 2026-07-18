from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user, get_current_user_for_write
from app.modules.users.models import User
from app.modules.watchlist.schemas import WatchlistActionResponse, WatchlistPage
from app.modules.watchlist.service import add_watchlist_item, list_watchlist_markets, remove_watchlist_item

router = APIRouter()


@router.get("", response_model=WatchlistPage)
def list_watchlist_endpoint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
  return {"items": list_watchlist_markets(db, user_id=user.id), "next_cursor": None}


@router.post("/{market_id}", response_model=WatchlistActionResponse)
def add_watchlist_endpoint(market_id: str, user: User = Depends(get_current_user_for_write), db: Session = Depends(get_db)):
  item = add_watchlist_item(db, user_id=user.id, market_id=market_id)
  db.commit()
  return {"market_id": item.market_id, "watchlisted": True}


@router.delete("/{market_id}", response_model=WatchlistActionResponse)
def remove_watchlist_endpoint(market_id: str, user: User = Depends(get_current_user_for_write), db: Session = Depends(get_db)):
  remove_watchlist_item(db, user_id=user.id, market_id=market_id)
  db.commit()
  return {"market_id": market_id, "watchlisted": False}
