import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.redis import get_redis
from app.db.session import get_db
from app.main import app
from app.modules.admin.models import AdminReview
from app.modules.analytics.models import CategoryAnalytics, MarketAnalytics, UserAnalytics
from app.modules.audit.models import AuditLog
from app.modules.auth.models import (
  AdminImpersonationSession,
  AuthSession,
  EmailVerificationToken,
  MfaRecoveryCode,
  PasswordResetToken,
  UserMfaFactor,
)
from app.modules.market_suggestions.models import MarketSuggestion
from app.modules.markets.models import Category, Market, MarketRule, OracleEvidence, Outcome
from app.modules.market_issuance.models import DataSource, MarketDraft, MarketDraftEvidence, SourceEvent
from app.modules.orders.models import Order
from app.modules.positions.models import Position
from app.modules.realtime.models import RealtimeEvent
from app.modules.settlement.models import ResolutionProposal, Settlement, SettlementItem
from app.modules.trades.models import Trade
from app.modules.users.models import User, UserRole
from app.modules.wallets.models import LedgerAccount, LedgerEntry, LedgerTransaction, Wallet
from app.modules.watchlist.models import WatchlistItem
from app.seed.dev import seed_database


@pytest.fixture()
def db_session():
  engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
  )
  TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
  Base.metadata.create_all(bind=engine)
  try:
    redis = get_redis()
    for key in redis.scan_iter("rate:*"):
      redis.delete(key)
  except Exception:
    pass

  with TestingSessionLocal() as db:
    seed_database(db)
    yield db

  Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session):
  def override_get_db():
    yield db_session

  app.dependency_overrides[get_db] = override_get_db
  with TestClient(app) as test_client:
    original_request = test_client.request

    def csrf_request(method: str, url: str, **kwargs):
      headers = dict(kwargs.pop("headers", {}) or {})
      if method.upper() in {"POST", "PUT", "PATCH", "DELETE"} and "X-CSRF-Token" not in headers:
        csrf_token = test_client.cookies.get("pred_market_v1_csrf_token")
        if csrf_token:
          headers["X-CSRF-Token"] = csrf_token
      return original_request(method, url, headers=headers, **kwargs)

    test_client.request = csrf_request
    yield test_client
  app.dependency_overrides.clear()


def sign_in(client: TestClient, email: str = "trader@predmarket.dev") -> TestClient:
  response = client.post("/api/v1/auth/sign-in", json={"email": email, "password": "StrongPass123"})
  assert response.status_code == 200
  return client
