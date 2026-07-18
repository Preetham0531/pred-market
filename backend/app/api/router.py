from fastapi import APIRouter

from app.modules.admin.router import router as admin_router
from app.modules.analytics.router import router as analytics_router
from app.modules.auth.router import router as auth_router
from app.modules.markets.router import router as markets_router
from app.modules.market_suggestions.router import router as suggestions_router
from app.modules.orders.router import router as orders_router
from app.modules.positions.router import router as positions_router
from app.modules.trades.router import router as trades_router
from app.modules.wallets.router import router as wallets_router
from app.modules.watchlist.router import router as watchlist_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(markets_router, tags=["markets"])
api_router.include_router(suggestions_router, prefix="/market-suggestions", tags=["market suggestions"])
api_router.include_router(wallets_router, prefix="/wallet", tags=["wallet"])
api_router.include_router(watchlist_router, prefix="/watchlist", tags=["watchlist"])
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])
api_router.include_router(trades_router, prefix="/trades", tags=["trades"])
api_router.include_router(positions_router, tags=["positions"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
