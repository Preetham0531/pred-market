from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.markets.schemas import (
  CategoryResponse,
  CategoryList,
  MarketDetail,
  OrderBookResponse,
  PaginatedMarkets,
  PriceHistoryResponse,
)
from app.modules.markets.service import (
  category_to_response,
  computed_order_book,
  computed_recent_trades,
  get_category_or_404,
  get_market_or_404,
  list_categories,
  list_markets,
  market_to_detail,
  market_to_list_item,
  order_book_snapshot,
)

router = APIRouter()


@router.get("/categories", response_model=CategoryList)
def categories_endpoint(db: Session = Depends(get_db)):
  return {"items": [category_to_response(category) for category in list_categories(db)], "next_cursor": None}


@router.get("/markets", response_model=PaginatedMarkets)
def markets_endpoint(
  category: str | None = None,
  status: str | None = None,
  q: str | None = None,
  limit: int = Query(default=50, ge=1, le=100),
  db: Session = Depends(get_db),
):
  markets = list_markets(db, category=category, status=status, q=q, limit=limit)
  return {"items": [market_to_list_item(db, market) for market in markets], "next_cursor": None}


@router.get("/markets/{market_id}", response_model=MarketDetail)
def market_detail_endpoint(market_id: str, db: Session = Depends(get_db)):
  market = get_market_or_404(db, market_id)
  return market_to_detail(db, market)


@router.get("/markets/{market_id}/order-book", response_model=OrderBookResponse)
def market_order_book_endpoint(market_id: str, db: Session = Depends(get_db)):
  market = get_market_or_404(db, market_id)
  return order_book_snapshot(db, market)


@router.get("/markets/{market_id}/price-history", response_model=PriceHistoryResponse)
def market_price_history_endpoint(market_id: str, db: Session = Depends(get_db)):
  market = get_market_or_404(db, market_id)
  return {"market_id": market.id, "points": market.price_history_json}


@router.get("/categories/{category_slug}", response_model=CategoryResponse)
def category_endpoint(category_slug: str, db: Session = Depends(get_db)):
  return category_to_response(get_category_or_404(db, category_slug))
