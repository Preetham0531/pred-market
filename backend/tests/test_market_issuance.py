from sqlalchemy import select

from app.modules.audit.models import AuditLog
from app.modules.markets.models import Market
from app.modules.market_issuance.models import DataSource, MarketDraft, SourceEvent


def sign_in_admin(client):
  response = client.post("/api/v1/auth/sign-in", json={"email": "admin@predmarket.dev", "password": "StrongPass123"})
  assert response.status_code == 200


def test_admin_can_list_data_sources(client):
  sign_in_admin(client)

  response = client.get("/api/v1/admin/data-sources")

  assert response.status_code == 200
  body = response.json()
  assert body["items"]
  assert any(item["settlement_eligible"] for item in body["items"])


def test_ingestion_run_saves_source_events_and_dedupes(client, db_session):
  sign_in_admin(client)

  first = client.post("/api/v1/admin/ingestion-runs", json={"category_slug": "tech-science", "query": "frontier AI model releases", "limit": 1})
  second = client.post("/api/v1/admin/ingestion-runs", json={"category_slug": "tech-science", "query": "frontier AI model releases", "limit": 1})

  assert first.status_code == 200
  assert first.json()["created_events"] == 1
  assert second.status_code == 200
  assert second.json()["skipped_duplicates"] == 1
  assert db_session.scalar(select(SourceEvent).where(SourceEvent.category_slug == "tech-science")) is not None


def test_ai_market_generation_creates_draft_but_not_market(client, db_session):
  sign_in_admin(client)
  assert client.post("/api/v1/admin/ingestion-runs", json={"category_slug": "tech-science", "query": "frontier AI model releases", "limit": 1}).status_code == 200

  generated = client.post("/api/v1/admin/ai-market-generation/run", json={"category_slug": "tech-science", "limit": 1})

  assert generated.status_code == 200
  assert generated.json()["created_drafts"] == 1
  draft = generated.json()["items"][0]
  assert draft["origin"] == "AI"
  assert draft["status"] == "NEEDS_CHANGES"
  assert draft["listed_market_id"] is None
  assert db_session.scalar(select(Market).where(Market.title == draft["question"])) is None


def test_admin_direct_create_lists_valid_market(client, db_session):
  sign_in_admin(client)
  source = db_session.scalar(select(DataSource).where(DataSource.category_slug == "sports", DataSource.settlement_eligible.is_(True)))

  response = client.post(
    "/api/v1/admin/market-drafts",
    json={
      "origin": "ADMIN",
      "category_slug": "sports",
      "subcategory": "Cricket",
      "market_type": "Binary",
      "question": "Will the official ICC source declare Team A winner in the demo match?",
      "outcomes": ["YES", "NO"],
      "close_time": "Aug 1, 2026 18:30 UTC",
      "source": source.name,
      "resolution_rule": "YES resolves if the approved ICC source declares Team A winner.",
      "void_policy": "Void only if the event is abandoned without an official result.",
      "settlement_source_id": source.id,
      "discovery_source_id": source.id,
      "list_immediately": True,
    },
  )

  assert response.status_code == 201
  body = response.json()
  assert body["status"] == "LISTED"
  assert body["listed_market_id"]
  assert db_session.get(Market, body["listed_market_id"]) is not None
  assert db_session.scalar(select(AuditLog).where(AuditLog.event_type == "MARKET_DRAFT_LISTED")) is not None


def test_draft_approval_requires_all_checks(client, db_session):
  sign_in_admin(client)
  source = db_session.scalar(select(DataSource).where(DataSource.category_slug == "sports", DataSource.settlement_eligible.is_(True)))

  created = client.post(
    "/api/v1/admin/market-drafts",
    json={
      "origin": "ADMIN",
      "category_slug": "sports",
      "subcategory": "Cricket",
      "market_type": "Binary",
      "question": "Will this demo draft wait for an exact close time?",
      "outcomes": ["YES", "NO"],
      "close_time": "Admin must set close time",
      "source": source.name,
      "resolution_rule": "YES resolves if the approved source confirms it.",
      "void_policy": "Void only if source unavailable.",
      "settlement_source_id": source.id,
      "discovery_source_id": source.id,
    },
  )
  assert created.status_code == 201

  approve = client.post(f"/api/v1/admin/market-drafts/{created.json()['id']}/approve")

  assert approve.status_code == 422
  assert approve.json()["error"]["code"] == "DRAFT_CHECKS_FAILED"


def test_admin_can_fix_and_approve_existing_draft_without_self_duplicate(client, db_session):
  sign_in_admin(client)
  source = db_session.scalar(select(DataSource).where(DataSource.category_slug == "sports", DataSource.settlement_eligible.is_(True)))

  created = client.post(
    "/api/v1/admin/market-drafts",
    json={
      "origin": "ADMIN",
      "category_slug": "sports",
      "subcategory": "Cricket",
      "market_type": "Binary",
      "question": "Will the corrected simulation draft pass its final review?",
      "outcomes": ["YES", "NO"],
      "close_time": "Admin must set close time",
      "source": source.name,
      "resolution_rule": "YES resolves if the approved source confirms the result.",
      "void_policy": "Void only if the approved source is unavailable.",
      "settlement_source_id": source.id,
      "discovery_source_id": source.id,
    },
  )
  assert created.status_code == 201
  assert created.json()["status"] == "NEEDS_CHANGES"

  updated = client.patch(
    f"/api/v1/admin/market-drafts/{created.json()['id']}",
    json={"close_time": "Dec 31, 2027 23:59 UTC"},
  )
  assert updated.status_code == 200
  assert updated.json()["status"] == "NEEDS_REVIEW"
  assert updated.json()["checks"]["duplicate_title"]["passed"] is True

  approved = client.post(f"/api/v1/admin/market-drafts/{created.json()['id']}/approve")
  assert approved.status_code == 200
  assert approved.json()["status"] == "APPROVED"


def test_trader_suggestion_creates_market_draft_and_review(client, db_session):
  assert client.post("/api/v1/auth/sign-in", json={"email": "trader@predmarket.dev", "password": "StrongPass123"}).status_code == 200

  response = client.post(
    "/api/v1/market-suggestions",
    json={
      "category_slug": "weather-climate",
      "market_type": "Binary",
      "question": "Will the official station record more than 10 mm rain in the demo window?",
      "outcomes": ["YES", "NO"],
      "source": "Official weather station report",
      "resolution_rule": "YES resolves if the official station reports more than 10 mm rain.",
    },
  )

  assert response.status_code == 201
  assert response.json()["draft_id"]
  assert db_session.scalar(select(MarketDraft).where(MarketDraft.suggestion_id.is_not(None))) is not None


def test_non_admin_cannot_access_issuing_apis(client):
  assert client.post("/api/v1/auth/sign-in", json={"email": "trader@predmarket.dev", "password": "StrongPass123"}).status_code == 200

  response = client.get("/api/v1/admin/market-drafts")

  assert response.status_code == 403
