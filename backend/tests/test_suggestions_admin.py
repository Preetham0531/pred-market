from sqlalchemy import select

from app.modules.audit.models import AuditLog
from app.modules.market_suggestions.models import MarketSuggestion
from app.modules.market_issuance.models import MarketDraft


def test_signed_in_user_can_create_and_read_suggestion(client, db_session):
  assert client.post("/api/v1/auth/sign-in", json={"email": "trader@predmarket.dev", "password": "StrongPass123"}).status_code == 200
  response = client.post(
    "/api/v1/market-suggestions",
    json={
      "category_slug": "sports",
      "market_type": "Binary",
      "question": "Will India win its next official cricket match?",
      "outcomes": ["YES", "NO"],
      "source": "Official tournament result page",
      "resolution_rule": "YES resolves if the official tournament source lists India as winner.",
    },
  )

  assert response.status_code == 201
  body = response.json()
  assert body["status"] == "NEEDS_CHANGES"
  assert body["draft_id"]
  assert body["checks"]["duplicate_title"]["passed"] is True
  assert db_session.scalar(select(MarketDraft).where(MarketDraft.question == body["question"])) is not None

  read_response = client.get(f"/api/v1/market-suggestions/{body['id']}")
  assert read_response.status_code == 200
  assert read_response.json()["id"] == body["id"]


def test_duplicate_suggestion_is_flagged(client):
  assert client.post("/api/v1/auth/sign-in", json={"email": "trader@predmarket.dev", "password": "StrongPass123"}).status_code == 200
  response = client.post(
    "/api/v1/market-suggestions",
    json={
      "category_slug": "sports",
      "market_type": "Binary",
      "question": "Will India beat Australia in the next T20 final?",
      "outcomes": ["YES", "NO"],
      "source": "Official tournament result page",
      "resolution_rule": "YES resolves if India is official winner.",
    },
  )

  assert response.status_code == 201
  assert response.json()["status"] == "NEEDS_CHANGES"
  assert response.json()["checks"]["duplicate_title"]["passed"] is False


def test_admin_can_review_approve_and_pause(client, db_session):
  assert client.post("/api/v1/auth/sign-in", json={"email": "admin@predmarket.dev", "password": "StrongPass123"}).status_code == 200

  queue = client.get("/api/v1/admin/markets/review")
  assert queue.status_code == 200
  assert queue.json()["items"]
  review_id = queue.json()["items"][0]["id"]

  detail = client.get(f"/api/v1/admin/markets/review/{review_id}")
  assert detail.status_code == 200
  assert detail.json()["id"] == review_id
  assert "created_at" in detail.json()
  assert "market_id" in detail.json()

  approve = client.post("/api/v1/admin/markets/ind-aus-final/approve")
  assert approve.status_code == 200
  assert approve.json()["status"] == "OPEN"

  pause = client.post("/api/v1/admin/markets/ind-aus-final/pause")
  assert pause.status_code == 200
  assert pause.json()["status"] == "PAUSED"

  assert db_session.scalar(select(AuditLog).where(AuditLog.event_type == "MARKET_PAUSED")) is not None
