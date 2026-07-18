from collections.abc import Iterable

from sqlalchemy import func, select

from app.core.public_ids import matches_public_id
from app.modules.audit.models import AuditLog
from app.modules.markets.models import Market
from app.modules.market_issuance.models import DataSource, MarketDraft
from app.modules.orders.models import Order
from app.modules.positions.models import Position
from app.modules.realtime.models import RealtimeEvent
from app.modules.settlement.models import Settlement
from app.modules.trades.models import Trade
from app.modules.users.models import User, UserRole
from app.modules.wallets.models import LedgerEntry, Wallet

PASSWORD = "StrongPass123"
AUTH_COOKIE_NAMES = [
  "pred_market_v1_access_token",
  "pred_market_v1_refresh_token",
  "pred_market_v1_csrf_token",
]


def capture_session(client) -> dict[str, str]:
  return {name: client.cookies.get(name) for name in AUTH_COOKIE_NAMES if client.cookies.get(name)}


def use_session(client, session: dict[str, str] | None) -> None:
  client.cookies.clear()
  if not session:
    return
  for name, value in session.items():
    client.cookies.set(name, value)


def sign_in(client, email: str) -> dict[str, str]:
  use_session(client, None)
  response = client.post("/api/v1/auth/sign-in", json={"email": email, "password": PASSWORD})
  assert response.status_code == 200
  return capture_session(client)


def sign_up_user(client, email: str) -> dict[str, str]:
  use_session(client, None)
  response = client.post(
    "/api/v1/auth/sign-up",
    json={
      "email": email,
      "password": PASSWORD,
      "display_name": email.split("@")[0],
      "terms_acceptance": True,
    },
  )
  assert response.status_code == 201
  assert response.json()["user"]["email"] == email
  return capture_session(client)


def deposit(client, session: dict[str, str], amount_minor: int, key: str):
  use_session(client, session)
  response = client.post(
    "/api/v1/wallet/test-deposit",
    json={"amount_minor": amount_minor, "currency": "INR"},
    headers={"Idempotency-Key": key},
  )
  assert response.status_code == 200
  return response


def source_for_category(client, admin_session: dict[str, str], category_slug: str) -> dict:
  use_session(client, admin_session)
  response = client.get("/api/v1/admin/data-sources", params={"category_slug": category_slug})
  assert response.status_code == 200
  source = next((item for item in response.json()["items"] if item["settlement_eligible"]), None)
  assert source is not None
  return source


def create_admin_source(client, admin_session: dict[str, str], *, category_slug: str, name: str) -> dict:
  use_session(client, admin_session)
  response = client.post(
    "/api/v1/admin/data-sources",
    json={
      "name": name,
      "provider": "Pred-Market test source",
      "source_type": "OFFICIAL",
      "category_slug": category_slug,
      "base_url": "https://example.com/pred-market-test-source",
      "license_status": "PUBLIC_OFFICIAL",
      "automation_level": 1,
      "refresh_schedule": "MANUAL",
      "settlement_eligible": True,
      "discovery_eligible": True,
      "notes": "Created by multi-user simulation test.",
    },
  )
  assert response.status_code == 201
  return response.json()


def create_admin_market(
  client,
  admin_session: dict[str, str],
  *,
  source: dict,
  category_slug: str,
  market_type: str,
  question: str,
) -> str:
  use_session(client, admin_session)
  response = client.post(
    "/api/v1/admin/market-drafts",
    json={
      "origin": "ADMIN",
      "category_slug": category_slug,
      "subcategory": "Simulation",
      "market_type": market_type,
      "question": question,
      "outcomes": ["YES", "NO"],
      "close_time": "Dec 31, 2026 23:59 UTC",
      "source": source["name"],
      "resolution_rule": f"YES resolves if {source['name']} confirms the event before the deadline. Otherwise NO resolves unless the void policy applies.",
      "void_policy": "Void only if the approved settlement source is unavailable or category rules require voiding.",
      "settlement_source_id": source["id"],
      "discovery_source_id": source["id"],
      "list_immediately": True,
    },
  )
  assert response.status_code == 201
  body = response.json()
  assert body["status"] == "LISTED"
  assert body["listed_market_id"]
  return body["listed_market_id"]


def place_order(
  client,
  session: dict[str, str] | None,
  *,
  market_id: str,
  outcome: str,
  price: int,
  quantity: int,
  key: str | None,
):
  use_session(client, session)
  headers = {"Idempotency-Key": key} if key else {}
  return client.post(
    "/api/v1/orders",
    json={"market_id": market_id, "outcome": outcome, "side": "BUY", "price_minor": price, "quantity": quantity},
    headers=headers,
  )


def resolve_public_order_id(db_session, order_id: str) -> Order:
  for order in db_session.scalars(select(Order)).all():
    if matches_public_id("ORD", order.id, order_id):
      return order
  raise AssertionError(f"Order {order_id} was not found")


def assert_ledger_balanced(db_session) -> None:
  entries = db_session.scalars(select(LedgerEntry)).all()
  debit_total = sum(entry.amount_minor for entry in entries if entry.side == "DEBIT")
  credit_total = sum(entry.amount_minor for entry in entries if entry.side == "CREDIT")
  assert debit_total == credit_total


def assert_users_exist_with_roles(db_session, emails: Iterable[str]) -> None:
  for email in emails:
    user = db_session.scalar(select(User).where(User.email == email))
    assert user is not None
    roles = {role.role for role in db_session.scalars(select(UserRole).where(UserRole.user_id == user.id)).all()}
    assert roles == {"USER"}


def create_simulation_markets(client, db_session, admin_session: dict[str, str]) -> list[str]:
  tech_source = create_admin_source(client, admin_session, category_slug="tech-science", name="Pred-Market official tech simulation source")
  source_by_category = {
    "sports": source_for_category(client, admin_session, "sports"),
    "economics": source_for_category(client, admin_session, "economics"),
    "weather-climate": source_for_category(client, admin_session, "weather-climate"),
    "tech-science": tech_source,
    "commodities": source_for_category(client, admin_session, "commodities"),
  }
  market_specs = [
    ("sports", "Binary", "Will the official simulation source declare Alpha Cricket Club winner?"),
    ("sports", "Binary", "Will the official simulation source declare Beta Football Club winner?"),
    ("economics", "Threshold", "Will the official simulation CPI release be above the test threshold?"),
    ("weather-climate", "Threshold", "Will the official simulation weather station exceed the rainfall threshold?"),
    ("tech-science", "Conditional", "Will the official simulation tech source announce a public model release?"),
    ("commodities", "Threshold", "Will the official simulation commodity benchmark settle above the test threshold?"),
  ]

  market_ids = [
    create_admin_market(
      client,
      admin_session,
      source=source_by_category[category_slug],
      category_slug=category_slug,
      market_type=market_type,
      question=question,
    )
    for category_slug, market_type, question in market_specs
  ]
  assert db_session.scalar(select(func.count(Market.id)).where(Market.id.in_(market_ids))) == 6
  return market_ids


def test_twenty_user_market_trading_day_happy_path(client, db_session):
  admin_session = sign_in(client, "admin@predmarket.dev")
  checker_session = sign_in(client, "checker@predmarket.dev")
  user_emails = [f"sim-user-{index:02d}@predmarket.dev" for index in range(1, 21)]
  user_sessions: dict[str, dict[str, str]] = {}

  for index, email in enumerate(user_emails, start=1):
    session = sign_up_user(client, email)
    user_sessions[email] = session
    deposit(client, session, 100_000, f"sim-deposit-{index:02d}")

  assert_users_exist_with_roles(db_session, user_emails)
  market_ids = create_simulation_markets(client, db_session, admin_session)

  filled_order_ids: list[str] = []
  for index in range(36):
    market_id = market_ids[index % len(market_ids)]
    yes_email = user_emails[index % len(user_emails)]
    no_email = user_emails[(index + 1) % len(user_emails)]
    quantity = 2 + (index % 3)
    yes_price = 40 + (index % 10)
    no_price = 100 - yes_price

    yes_order = place_order(
      client,
      user_sessions[yes_email],
      market_id=market_id,
      outcome="YES",
      price=yes_price,
      quantity=quantity,
      key=f"sim-match-{index:02d}-yes",
    )
    assert yes_order.status_code == 201
    assert yes_order.json()["status"] == "OPEN"

    no_order = place_order(
      client,
      user_sessions[no_email],
      market_id=market_id,
      outcome="NO",
      price=no_price,
      quantity=quantity,
      key=f"sim-match-{index:02d}-no",
    )
    assert no_order.status_code == 201
    assert no_order.json()["status"] == "FILLED"
    filled_order_ids.extend([yes_order.json()["id"], no_order.json()["id"]])

  partial_resting = place_order(
    client,
    user_sessions[user_emails[0]],
    market_id=market_ids[1],
    outcome="YES",
    price=45,
    quantity=10,
    key="sim-partial-yes",
  )
  assert partial_resting.status_code == 201
  partial_incoming = place_order(
    client,
    user_sessions[user_emails[1]],
    market_id=market_ids[1],
    outcome="NO",
    price=55,
    quantity=4,
    key="sim-partial-no",
  )
  assert partial_incoming.status_code == 201
  assert partial_incoming.json()["status"] == "FILLED"
  resting_after_partial = resolve_public_order_id(db_session, partial_resting.json()["id"])
  assert resting_after_partial.status == "PARTIALLY_FILLED"
  assert resting_after_partial.remaining_quantity == 6

  unmatched = place_order(
    client,
    user_sessions[user_emails[2]],
    market_id=market_ids[2],
    outcome="YES",
    price=25,
    quantity=8,
    key="sim-unmatched-open",
  )
  assert unmatched.status_code == 201
  assert unmatched.json()["status"] == "OPEN"

  use_session(client, user_sessions[user_emails[2]])
  wallet_after_unmatched = client.get("/api/v1/wallet").json()
  assert wallet_after_unmatched["locked"]["amount_minor"] >= 25 * 8

  cancelled = client.post(f"/api/v1/orders/{unmatched.json()['id']}/cancel")
  assert cancelled.status_code == 200
  assert cancelled.json()["status"] == "CANCELLED"
  wallet_after_cancel = client.get("/api/v1/wallet").json()
  assert wallet_after_cancel["locked"]["amount_minor"] < wallet_after_unmatched["locked"]["amount_minor"]

  order_book = client.get(f"/api/v1/markets/{market_ids[1]}/order-book")
  assert order_book.status_code == 200
  assert order_book.json()["order_book"]["yes_bids"]

  market_detail = client.get(f"/api/v1/markets/{market_ids[0]}")
  assert market_detail.status_code == 200
  assert market_detail.json()["recent_trades"]

  for public_id in filled_order_ids[:6]:
    assert resolve_public_order_id(db_session, public_id).status == "FILLED"
  assert db_session.scalar(select(func.count(Trade.id)).where(Trade.market_id.in_(market_ids))) >= 36
  assert db_session.scalar(select(func.count(Position.id)).where(Position.market_id.in_(market_ids))) >= 40

  use_session(client, admin_session)
  close = client.post(f"/api/v1/admin/markets/{market_ids[0]}/close")
  assert close.status_code == 200
  evidence = client.post(
    f"/api/v1/admin/markets/{market_ids[0]}/evidence",
    json={"source_name": "Simulation official source", "captured_payload": {"winner": "YES"}},
  )
  assert evidence.status_code == 201
  yes_outcome_id = next(outcome["id"] for outcome in client.get(f"/api/v1/markets/{market_ids[0]}").json()["outcomes"] if outcome["label"] == "YES")
  proposal = client.post(
    f"/api/v1/admin/markets/{market_ids[0]}/resolution-proposals",
    json={"result": "RESOLVE", "winning_outcome_id": yes_outcome_id, "reason": "Simulation source resolves YES."},
  )
  assert proposal.status_code == 201

  use_session(client, checker_session)
  approval = client.post(f"/api/v1/admin/resolution-proposals/{proposal.json()['id']}/approve")
  assert approval.status_code == 200
  settlement = client.post(f"/api/v1/admin/markets/{market_ids[0]}/settle", headers={"Idempotency-Key": "sim-settlement-1"})
  assert settlement.status_code == 200
  assert settlement.json()["status"] == "COMPLETE"
  assert any(item["payout_minor"] > 0 for item in settlement.json()["items"])
  assert any(item["payout_minor"] == 0 for item in settlement.json()["items"])

  assert db_session.scalar(select(Settlement).where(Settlement.market_id == market_ids[0])) is not None
  assert db_session.scalar(select(func.count(Order.id)).where(Order.market_id.in_(market_ids))) >= 75
  assert db_session.scalar(select(func.count(AuditLog.id)).where(AuditLog.event_type.in_(["MARKET_DRAFT_LISTED", "ORDER_CREATED", "ORDER_CANCELLED", "MARKET_SETTLED"]))) >= 4
  assert db_session.scalar(select(func.count(RealtimeEvent.id))) > 0
  assert_ledger_balanced(db_session)


def test_multi_user_negative_paths(client, db_session):
  admin_session = sign_in(client, "admin@predmarket.dev")
  trader_session = sign_in(client, "trader@predmarket.dev")
  checker_session = sign_in(client, "checker@predmarket.dev")
  other_user_session = sign_up_user(client, "negative-other-user@predmarket.dev")
  deposit(client, trader_session, 10_000, "negative-trader-deposit")
  market_ids = create_simulation_markets(client, db_session, admin_session)
  sports_source = source_for_category(client, admin_session, "sports")

  unauthenticated = place_order(client, None, market_id=market_ids[0], outcome="YES", price=40, quantity=1, key="negative-unauth")
  assert unauthenticated.status_code == 401

  use_session(client, trader_session)
  forbidden_draft = client.post(
    "/api/v1/admin/market-drafts",
    json={
      "origin": "ADMIN",
      "category_slug": "sports",
      "market_type": "Binary",
      "question": "Will a normal user create an admin-only market?",
      "outcomes": ["YES", "NO"],
      "close_time": "Dec 31, 2026 23:59 UTC",
      "source": sports_source["name"],
      "resolution_rule": "YES resolves if the approved source confirms it.",
      "settlement_source_id": sports_source["id"],
    },
  )
  assert forbidden_draft.status_code == 403

  use_session(client, admin_session)
  duplicate = client.post(
    "/api/v1/admin/market-drafts",
    json={
      "origin": "ADMIN",
      "category_slug": "sports",
      "subcategory": "Simulation",
      "market_type": "Binary",
      "question": "Will India beat Australia in the next T20 final?",
      "outcomes": ["YES", "NO"],
      "close_time": "Dec 31, 2026 23:59 UTC",
      "source": sports_source["name"],
      "resolution_rule": "YES resolves if the approved source confirms it.",
      "void_policy": "Void only if source unavailable.",
      "settlement_source_id": sports_source["id"],
      "discovery_source_id": sports_source["id"],
    },
  )
  assert duplicate.status_code == 201
  assert duplicate.json()["status"] == "NEEDS_CHANGES"
  assert duplicate.json()["checks"]["duplicate_title"]["passed"] is False

  no_source = client.post(
    "/api/v1/admin/market-drafts",
    json={
      "origin": "ADMIN",
      "category_slug": "sports",
      "subcategory": "Simulation",
      "market_type": "Binary",
      "question": "Will an admin draft without approved source be listed?",
      "outcomes": ["YES", "NO"],
      "close_time": "Dec 31, 2026 23:59 UTC",
      "source": "Unapproved source",
      "resolution_rule": "YES resolves if an unapproved source confirms it.",
      "void_policy": "Void only if source unavailable.",
    },
  )
  assert no_source.status_code == 201
  assert no_source.json()["status"] == "NEEDS_CHANGES"
  approve_no_source = client.post(f"/api/v1/admin/market-drafts/{no_source.json()['id']}/approve")
  assert approve_no_source.status_code == 422
  assert approve_no_source.json()["error"]["code"] == "DRAFT_CHECKS_FAILED"

  invalid_price_low = place_order(client, trader_session, market_id=market_ids[0], outcome="YES", price=0, quantity=1, key="negative-price-low")
  invalid_price_high = place_order(client, trader_session, market_id=market_ids[0], outcome="YES", price=100, quantity=1, key="negative-price-high")
  invalid_quantity = place_order(client, trader_session, market_id=market_ids[0], outcome="YES", price=40, quantity=0, key="negative-qty")
  assert invalid_price_low.status_code == 422
  assert invalid_price_high.status_code == 422
  assert invalid_quantity.status_code == 422

  insufficient = place_order(client, trader_session, market_id=market_ids[0], outcome="YES", price=99, quantity=100_000, key="negative-insufficient")
  assert insufficient.status_code == 402
  assert insufficient.json()["error"]["code"] == "INSUFFICIENT_FUNDS"

  open_order = place_order(client, trader_session, market_id=market_ids[0], outcome="YES", price=20, quantity=3, key="negative-owner-order")
  assert open_order.status_code == 201
  use_session(client, other_user_session)
  non_owner_cancel = client.post(f"/api/v1/orders/{open_order.json()['id']}/cancel")
  assert non_owner_cancel.status_code == 403

  use_session(client, trader_session)
  self_yes = place_order(client, trader_session, market_id=market_ids[1], outcome="YES", price=40, quantity=5, key="negative-self-yes")
  self_no = place_order(client, trader_session, market_id=market_ids[1], outcome="NO", price=60, quantity=5, key="negative-self-no")
  assert self_yes.status_code == 201
  assert self_no.status_code == 201
  assert self_yes.json()["status"] == "OPEN"
  assert self_no.json()["status"] == "OPEN"
  assert db_session.scalar(select(Trade).where(Trade.market_id == market_ids[1])) is None

  idempotent_first = place_order(client, trader_session, market_id=market_ids[2], outcome="YES", price=31, quantity=2, key="negative-idempotent")
  idempotent_second = place_order(client, trader_session, market_id=market_ids[2], outcome="YES", price=31, quantity=2, key="negative-idempotent")
  assert idempotent_first.status_code == 201
  assert idempotent_second.status_code == 201
  assert idempotent_first.json()["id"] == idempotent_second.json()["id"]
  assert db_session.scalar(select(func.count(Order.id)).where(Order.idempotency_key == "negative-idempotent")) == 1

  use_session(client, admin_session)
  close = client.post(f"/api/v1/admin/markets/{market_ids[3]}/close")
  assert close.status_code == 200
  closed_order = place_order(client, trader_session, market_id=market_ids[3], outcome="YES", price=40, quantity=1, key="negative-closed")
  assert closed_order.status_code == 422
  assert closed_order.json()["error"]["code"] == "MARKET_NOT_OPEN"

  missing_idempotency = place_order(client, trader_session, market_id=market_ids[4], outcome="YES", price=40, quantity=1, key=None)
  assert missing_idempotency.status_code == 400
  assert missing_idempotency.json()["error"]["code"] == "IDEMPOTENCY_KEY_REQUIRED"

  suggestion = client.post(
    "/api/v1/market-suggestions",
    json={
      "category_slug": "weather-climate",
      "market_type": "Binary",
      "question": "Will the simulation trader suggestion become listed automatically?",
      "outcomes": ["YES", "NO"],
      "source": "Official weather station report",
      "resolution_rule": "YES resolves if the official station confirms it.",
    },
  )
  assert suggestion.status_code == 201
  draft = db_session.scalar(select(MarketDraft).where(MarketDraft.question == suggestion.json()["question"]))
  assert draft is not None
  assert draft.listed_market_id is None

  assert_ledger_balanced(db_session)
