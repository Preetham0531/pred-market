from sqlalchemy import select

from app.modules.analytics.models import MarketAnalytics, UserAnalytics
from app.modules.realtime.models import RealtimeEvent


def sign_in(client, email: str = "trader@predmarket.dev"):
  response = client.post("/api/v1/auth/sign-in", json={"email": email, "password": "StrongPass123"})
  assert response.status_code == 200


def test_analytics_endpoints_compute_market_category_and_user(client, db_session):
  sign_in(client)
  assert client.post("/api/v1/wallet/test-deposit", json={"amount_minor": 50000}, headers={"Idempotency-Key": "phase7-dep"}).status_code == 200
  assert client.post(
    "/api/v1/orders",
    json={"market_id": "ind-aus-final", "outcome": "YES", "side": "BUY", "price_minor": 42, "quantity": 12},
    headers={"Idempotency-Key": "phase7-order"},
  ).status_code == 201

  market = client.get("/api/v1/analytics/markets/ind-aus-final")
  category = client.get("/api/v1/analytics/categories/sports")
  user = client.get("/api/v1/analytics/users/me")

  assert market.status_code == 200
  assert market.json()["best_bid"] == 42
  assert market.json()["liquidity_depth"] >= 12
  assert category.status_code == 200
  assert category.json()["active_markets"] >= 1
  assert user.status_code == 200
  assert user.json()["locked_cash"] == 504
  assert db_session.scalar(select(MarketAnalytics).where(MarketAnalytics.market_id == "ind-aus-final")) is not None
  assert db_session.scalar(select(UserAnalytics)) is not None


def test_order_and_wallet_flows_write_realtime_events(client, db_session):
  sign_in(client)
  assert client.post("/api/v1/wallet/test-deposit", json={"amount_minor": 50000}, headers={"Idempotency-Key": "phase7-event-dep"}).status_code == 200
  order = client.post(
    "/api/v1/orders",
    json={"market_id": "ind-aus-final", "outcome": "YES", "side": "BUY", "price_minor": 41, "quantity": 5},
    headers={"Idempotency-Key": "phase7-event-order"},
  )
  assert order.status_code == 201
  assert client.post(f"/api/v1/orders/{order.json()['id']}/cancel").status_code == 200

  event_types = {event.event_type for event in db_session.scalars(select(RealtimeEvent)).all()}
  assert "wallet.updated" in event_types
  assert "order.updated" in event_types
  assert "order_book.delta" in event_types


def test_computed_order_book_uses_live_orders_before_seeded_fallback(client):
  sign_in(client)
  assert client.post("/api/v1/wallet/test-deposit", json={"amount_minor": 50000}, headers={"Idempotency-Key": "phase7-book-dep"}).status_code == 200
  assert client.post(
    "/api/v1/orders",
    json={"market_id": "ind-aus-final", "outcome": "YES", "side": "BUY", "price_minor": 39, "quantity": 7},
    headers={"Idempotency-Key": "phase7-book-order"},
  ).status_code == 201

  response = client.get("/api/v1/markets/ind-aus-final/order-book")

  assert response.status_code == 200
  assert response.json()["order_book"]["yes_bids"][0] == {"price": 39, "quantity": 7}


def test_websocket_public_and_private_subscriptions(client):
  with client.websocket_connect("/ws/v1") as websocket:
    websocket.send_json({"type": "subscribe", "channel": "market.order_book", "market_id": "ind-aus-final"})
    assert websocket.receive_json()["type"] == "subscribed"
    snapshot = websocket.receive_json()
    assert snapshot["event_type"] == "order_book.snapshot"
    assert snapshot["market_id"] == "ind-aus-final"
    websocket.send_json({"type": "subscribe", "channel": "user.wallet"})
    assert websocket.receive_json()["code"] == "FORBIDDEN"

  sign_in(client)
  ticket = client.post("/api/v1/auth/ws-ticket").json()["ticket"]
  with client.websocket_connect(f"/ws/v1?ticket={ticket}") as websocket:
    websocket.send_json({"type": "subscribe", "channel": "user.wallet"})
    message = websocket.receive_json()
    assert message["type"] == "subscribed"
    assert message["resolved_channel"].startswith("user.wallet.")


def test_admin_recompute_endpoint(client):
  sign_in(client, "admin@predmarket.dev")
  response = client.post("/api/v1/admin/analytics/recompute")

  assert response.status_code == 200
  assert response.json()["status"] == "complete"
  assert response.json()["markets"] >= 5
