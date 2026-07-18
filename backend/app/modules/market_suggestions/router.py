from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user, get_current_user_for_write
from app.modules.market_suggestions.schemas import MarketSuggestionCreate, MarketSuggestionResponse
from app.modules.market_suggestions.service import create_suggestion, get_suggestion_or_404, suggestion_to_response
from app.modules.users.models import User

router = APIRouter()


@router.post("", response_model=MarketSuggestionResponse, status_code=201)
def create_market_suggestion_endpoint(
  payload: MarketSuggestionCreate,
  request: Request,
  user: User = Depends(get_current_user_for_write),
  db: Session = Depends(get_db),
):
  suggestion = create_suggestion(db, payload=payload, user=user, request_id=getattr(request.state, "request_id", None))
  db.commit()
  return suggestion_to_response(suggestion)


@router.get("/{suggestion_id}", response_model=MarketSuggestionResponse)
def get_market_suggestion_endpoint(
  suggestion_id: str,
  user: User = Depends(get_current_user),
  db: Session = Depends(get_db),
):
  return suggestion_to_response(get_suggestion_or_404(db, suggestion_id, user))
