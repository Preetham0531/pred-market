from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.analytics.schemas import CategoryAnalyticsResponse, MarketAnalyticsResponse, UserAnalyticsResponse
from app.modules.analytics.service import (
  category_analytics_to_response,
  get_category_analytics,
  get_market_analytics,
  get_user_analytics,
  market_analytics_to_response,
  user_analytics_to_response,
)
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User

router = APIRouter()


@router.get("/markets/{market_id}", response_model=MarketAnalyticsResponse)
def market_analytics_endpoint(market_id: str, db: Session = Depends(get_db)):
  row = get_market_analytics(db, market_id)
  db.commit()
  return market_analytics_to_response(row)


@router.get("/categories/{category_slug}", response_model=CategoryAnalyticsResponse)
def category_analytics_endpoint(category_slug: str, db: Session = Depends(get_db)):
  row = get_category_analytics(db, category_slug)
  db.commit()
  return category_analytics_to_response(row)


@router.get("/users/me", response_model=UserAnalyticsResponse)
def user_analytics_endpoint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
  row = get_user_analytics(db, user.id)
  db.commit()
  return user_analytics_to_response(row)
