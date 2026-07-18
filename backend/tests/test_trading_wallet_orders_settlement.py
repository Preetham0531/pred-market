from sqlalchemy import select

from app.core.public_ids import matches_public_id
from app.modules.audit.models import AuditLog
from app.modules.markets.models import Market
from app.modules.orders.models import Order
from app.modules.positions.models import Position
from app.modules.settlement.models import Settlement
from app.modules.trades.models import Trade
from app.modules.wallets.models import LedgerEntry, LedgerTransaction


def sign_in(client, email: str):
  response = client.post("/api/v1/auth/sign-in", json={"email": email, "password": "StrongPass123"})
  assert response.status_code == 200


def order_by_public_id(db_session, order_id: str) -> Order:
  for order in db_session.scalars(select(Order)).all():
    if matches_public_id("ORD", order.id, order_id):
      return order
  raise AssertionError(f"Order {order_id} was not found")


def test_wallet_test_deposit_is_idempotent_and_writes_balanced_ledger(client, db_session):
  sign_in(client, "trader@predmarket.dev")

  first = client.post("/api/v1/wallet/test-deposit", json={"amount_minor": 25000}, headers={"Idempotency-Key": "dep-1"})
  second = client.post("/api/v1/wallet/test-deposit", json={"amount_minor": 25000}, headers={"Idempotency-Key": "dep-1"})

  assert first.status_code == 200
  assert second.status_code == 200
  assert second.json()["available"]["amount_minor"] == 25000
  assert db_session.scalar(select(LedgerTransaction).where(LedgerTransaction.idempotency_key == "dep-1")) is not None
  entries = db_session.scalars(select(LedgerEntry)).all()
  debit_total = sum(entry.amount_minor for entry in entries if entry.side == "DEBIT")
  credit_total = sum(entry.amount_minor for entry in entries if entry.side == "CREDIT")
  assert debit_total == credit_total


def test_buy_order_locks_cash_and_cancel_releases_it(client, db_session):
  sign_in(client, "trader@predmarket.dev")
  assert client.post("/api/v1/wallet/test-deposit", json={"amount_minor": 10000}, headers={"Idempotency-Key": "dep-2"}).status_code == 200

  order = client.post(
    "/api/v1/orders",
    json={"market_id": "ind-aus-final", "outcome": "YES", "side": "BUY", "price_minor": 40, "quantity": 10},
    headers={"Idempotency-Key": "order-lock-1"},
  )

  assert order.status_code == 201
  assert order.json()["locked_cash_minor"] == 400
  wallet_after_order = client.get("/api/v1/wallet").json()
  assert wallet_after_order["available"]["amount_minor"] == 9600
  assert wallet_after_order["locked"]["amount_minor"] == 400

  cancel = client.post(f"/api/v1/orders/{order.json()['id']}/cancel")
  assert cancel.status_code == 200
  assert cancel.json()["status"] == "CANCELLED"
  wallet_after_cancel = client.get("/api/v1/wallet").json()
  assert wallet_after_cancel["available"]["amount_minor"] == 10000
  assert wallet_after_cancel["locked"]["amount_minor"] == 0
  assert db_session.scalar(select(AuditLog).where(AuditLog.event_type == "ORDER_CANCELLED")) is not None


def test_binary_yes_no_orders_match_and_create_positions(client, db_session):
  sign_in(client, "trader@predmarket.dev")
  assert client.post("/api/v1/wallet/test-deposit", json={"amount_minor": 100000}, headers={"Idempotency-Key": "dep-trader"}).status_code == 200
  trader_order = client.post(
    "/api/v1/orders",
    json={"market_id": "ind-aus-final", "outcome": "YES", "side": "BUY", "price_minor": 40, "quantity": 10},
    headers={"Idempotency-Key": "binary-yes"},
  )
  assert trader_order.status_code == 201
  assert trader_order.json()["status"] == "OPEN"

  sign_in(client, "admin@predmarket.dev")
  assert client.post("/api/v1/wallet/test-deposit", json={"amount_minor": 100000}, headers={"Idempotency-Key": "dep-admin"}).status_code == 200
  admin_order = client.post(
    "/api/v1/orders",
    json={"market_id": "ind-aus-final", "outcome": "NO", "side": "BUY", "price_minor": 60, "quantity": 10},
    headers={"Idempotency-Key": "binary-no"},
  )

  assert admin_order.status_code == 201
  assert admin_order.json()["status"] == "FILLED"
  assert db_session.scalar(select(Trade).where(Trade.market_id == "ind-aus-final")) is not None
  assert order_by_public_id(db_session, trader_order.json()["id"]).status == "FILLED"
  positions = db_session.scalars(select(Position).where(Position.market_id == "ind-aus-final")).all()
  assert sorted(position.quantity for position in positions) == [10, 10]

  admin_wallet = client.get("/api/v1/wallet").json()
  assert admin_wallet["available"]["amount_minor"] == 99400
  assert admin_wallet["locked"]["amount_minor"] == 0


def test_resolution_requires_maker_checker_and_settlement_pays_winner(client, db_session):
  sign_in(client, "trader@predmarket.dev")
  assert client.post("/api/v1/wallet/test-deposit", json={"amount_minor": 100000}, headers={"Idempotency-Key": "dep-settle-trader"}).status_code == 200
  assert client.post(
    "/api/v1/orders",
    json={"market_id": "ind-aus-final", "outcome": "YES", "side": "BUY", "price_minor": 40, "quantity": 10},
    headers={"Idempotency-Key": "settle-yes"},
  ).status_code == 201

  sign_in(client, "admin@predmarket.dev")
  assert client.post("/api/v1/wallet/test-deposit", json={"amount_minor": 100000}, headers={"Idempotency-Key": "dep-settle-admin"}).status_code == 200
  assert client.post(
    "/api/v1/orders",
    json={"market_id": "ind-aus-final", "outcome": "NO", "side": "BUY", "price_minor": 60, "quantity": 10},
    headers={"Idempotency-Key": "settle-no"},
  ).status_code == 201

  close = client.post("/api/v1/admin/markets/ind-aus-final/close")
  assert close.status_code == 200
  assert close.json()["status"] == "CLOSED"

  evidence = client.post(
    "/api/v1/admin/markets/ind-aus-final/evidence",
    json={"source_name": "Official tournament result", "captured_payload": {"winner": "India"}},
  )
  assert evidence.status_code == 201

  market_detail = client.get("/api/v1/markets/ind-aus-final").json()
  yes_outcome_id = next(outcome["id"] for outcome in market_detail["outcomes"] if outcome["label"] == "YES")
  proposal = client.post(
    "/api/v1/admin/markets/ind-aus-final/resolution-proposals",
    json={"result": "RESOLVE", "winning_outcome_id": yes_outcome_id, "reason": "Official source declares India as winner."},
  )
  assert proposal.status_code == 201

  same_admin_approval = client.post(f"/api/v1/admin/resolution-proposals/{proposal.json()['id']}/approve")
  assert same_admin_approval.status_code == 403

  sign_in(client, "checker@predmarket.dev")
  approval = client.post(f"/api/v1/admin/resolution-proposals/{proposal.json()['id']}/approve")
  assert approval.status_code == 200
  assert approval.json()["status"] == "APPROVED"

  settlement = client.post("/api/v1/admin/markets/ind-aus-final/settle", headers={"Idempotency-Key": "settle-1"})
  assert settlement.status_code == 200
  body = settlement.json()
  assert body["status"] == "COMPLETE"
  assert sorted(item["payout_minor"] for item in body["items"]) == [0, 1000]
  assert db_session.scalar(select(Settlement).where(Settlement.market_id == "ind-aus-final")) is not None
  assert db_session.get(Market, "ind-aus-final").status == "RESOLVED"

  sign_in(client, "trader@predmarket.dev")
  wallet = client.get("/api/v1/wallet").json()
  assert wallet["available"]["amount_minor"] == 100600
  assert db_session.scalar(select(AuditLog).where(AuditLog.event_type == "MARKET_SETTLED")) is not None
