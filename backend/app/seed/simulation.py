"""Persist a deterministic multi-user trading simulation in the local database.

This runner intentionally calls the live FastAPI HTTP API for all product actions,
then verifies the resulting PostgreSQL records directly. It is development-only.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any

import httpx
from sqlalchemy import func, select

from app.core.config import settings
from app.db.session import SessionLocal
from app.modules.audit.models import AuditLog
from app.modules.markets.models import Market
from app.modules.market_issuance.models import DataSource, MarketDraft
from app.modules.orders.models import Order
from app.modules.positions.models import Position
from app.modules.realtime.models import RealtimeEvent
from app.modules.settlement.models import Settlement
from app.modules.trades.models import Trade
from app.modules.users.models import User
from app.modules.wallets.models import LedgerEntry, Wallet

PASSWORD = "StrongPass123"
DEFAULT_API_BASE_URL = "http://127.0.0.1:8010"
CSRF_COOKIE = "pred_market_v1_csrf_token"
USER_EMAILS = [f"sim-user-{index:02d}@predmarket.dev" for index in range(1, 21)]


@dataclass(frozen=True)
class MarketSpec:
  category_slug: str
  market_type: str
  question: str


MARKET_SPECS = [
  MarketSpec("sports", "Binary", "Will Alpha Cricket Club win the persistent simulation final?"),
  MarketSpec("sports", "Binary", "Will Beta Football Club win the persistent simulation cup?"),
  MarketSpec("economics", "Threshold", "Will the persistent simulation CPI release exceed 4 percent?"),
  MarketSpec("weather-climate", "Threshold", "Will persistent simulation rainfall exceed 20 millimetres?"),
  MarketSpec("tech-science", "Conditional", "Will a public AI model launch in the persistent simulation window?"),
  MarketSpec("commodities", "Threshold", "Will the persistent simulation commodity benchmark exceed 2500?"),
]


class SimulationFailure(RuntimeError):
  pass


class ApiSession:
  def __init__(self, base_url: str):
    self.client = httpx.Client(base_url=base_url, timeout=30.0)

  def close(self) -> None:
    self.client.close()

  def request(
    self,
    method: str,
    path: str,
    *,
    expected: set[int] | None = None,
    headers: dict[str, str] | None = None,
    **kwargs: Any,
  ) -> httpx.Response:
    request_headers = dict(headers or {})
    if method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
      csrf_token = self.client.cookies.get(CSRF_COOKIE)
      if csrf_token:
        request_headers.setdefault("X-CSRF-Token", csrf_token)
    response = self.client.request(method, path, headers=request_headers, **kwargs)
    accepted = expected or {200}
    if response.status_code not in accepted:
      try:
        detail = response.json()
      except ValueError:
        detail = response.text
      raise SimulationFailure(f"{method} {path} returned {response.status_code}: {detail}")
    return response

  def get(self, path: str, *, expected: set[int] | None = None, **kwargs: Any) -> httpx.Response:
    return self.request("GET", path, expected=expected, **kwargs)

  def post(self, path: str, *, expected: set[int] | None = None, **kwargs: Any) -> httpx.Response:
    return self.request("POST", path, expected=expected, **kwargs)


def authenticate(base_url: str, email: str, *, create: bool = False) -> ApiSession:
  session = ApiSession(base_url)
  if create:
    sign_in_response = session.post(
      "/api/v1/auth/sign-in",
      expected={200, 401},
      json={"email": email, "password": PASSWORD},
    )
    if sign_in_response.status_code == 200:
      return session
    response = session.post(
      "/api/v1/auth/sign-up",
      expected={201, 409},
      json={
        "email": email,
        "password": PASSWORD,
        "display_name": email.split("@")[0],
        "terms_acceptance": True,
      },
    )
    if response.status_code == 201:
      return session
  session.post("/api/v1/auth/sign-in", json={"email": email, "password": PASSWORD})
  return session


def settlement_source(admin: ApiSession, category_slug: str) -> dict[str, Any]:
  response = admin.get("/api/v1/admin/data-sources", params={"category_slug": category_slug})
  source = next(
    (
      item
      for item in response.json()["items"]
      if item["settlement_eligible"] and item["license_status"] in {"APPROVED", "PUBLIC_OFFICIAL", "LICENSED"}
    ),
    None,
  )
  if source:
    return source

  name = f"Persistent simulation official source ({category_slug})"
  created = admin.post(
    "/api/v1/admin/data-sources",
    expected={201, 409},
    json={
      "name": name,
      "provider": "Pred-Market local simulation",
      "source_type": "OFFICIAL",
      "category_slug": category_slug,
      "base_url": f"https://example.com/pred-market-simulation/{category_slug}",
      "license_status": "PUBLIC_OFFICIAL",
      "automation_level": 1,
      "refresh_schedule": "MANUAL",
      "settlement_eligible": True,
      "discovery_eligible": True,
      "notes": "Development-only source used by the persistent trading simulation.",
    },
  )
  if created.status_code == 201:
    return created.json()
  response = admin.get("/api/v1/admin/data-sources", params={"category_slug": category_slug})
  return next(item for item in response.json()["items"] if item["name"] == name)


def existing_market_id(public: ApiSession, question: str) -> str | None:
  response = public.get("/api/v1/markets", params={"q": question, "limit": 100})
  market = next((item for item in response.json()["items"] if item["title"] == question), None)
  return market["id"] if market else None


def create_markets(admin: ApiSession, public: ApiSession) -> list[str]:
  sources = {spec.category_slug: settlement_source(admin, spec.category_slug) for spec in MARKET_SPECS}
  existing_drafts = admin.get("/api/v1/admin/market-drafts", params={"limit": 250}).json()["items"]
  market_ids: list[str] = []
  for spec in MARKET_SPECS:
    current_id = existing_market_id(public, spec.question)
    if current_id:
      market_ids.append(current_id)
      continue
    source = sources[spec.category_slug]
    existing_draft = next((item for item in existing_drafts if item["question"] == spec.question), None)
    if existing_draft:
      draft = admin.request(
        "PATCH",
        f"/api/v1/admin/market-drafts/{existing_draft['id']}",
        json={
          "source": source["name"],
          "settlement_source_id": source["id"],
          "discovery_source_id": source["id"],
          "resolution_rule": f"YES resolves if {source['name']} confirms the event before the deadline. Otherwise NO resolves unless the void policy applies.",
          "void_policy": "Void only if the approved settlement source is unavailable or the category rulebook requires voiding.",
        },
      ).json()
      if draft["status"] != "APPROVED":
        approved = admin.post(f"/api/v1/admin/market-drafts/{draft['id']}/approve").json()
        if approved["status"] != "APPROVED":
          raise SimulationFailure(f"Existing draft could not be approved: {approved}")
      listed = admin.post(f"/api/v1/admin/market-drafts/{draft['id']}/list").json()
      if listed["status"] != "LISTED" or not listed["market_id"]:
        raise SimulationFailure(f"Existing draft could not be listed: {listed}")
      market_ids.append(listed["market_id"])
      continue
    response = admin.post(
      "/api/v1/admin/market-drafts",
      expected={201},
      json={
        "origin": "ADMIN",
        "category_slug": spec.category_slug,
        "subcategory": "Persistent simulation",
        "market_type": spec.market_type,
        "question": spec.question,
        "outcomes": ["YES", "NO"],
        "close_time": "Dec 31, 2027 23:59 UTC",
        "source": source["name"],
        "resolution_rule": f"YES resolves if {source['name']} confirms the event before the deadline. Otherwise NO resolves unless the void policy applies.",
        "void_policy": "Void only if the approved settlement source is unavailable or the category rulebook requires voiding.",
        "settlement_source_id": source["id"],
        "discovery_source_id": source["id"],
        "admin_notes": "Created by the persistent real-database simulation.",
        "list_immediately": True,
      },
    )
    payload = response.json()
    if payload["status"] != "LISTED" or not payload["listed_market_id"]:
      raise SimulationFailure(f"Market was not listed: {payload}")
    market_ids.append(payload["listed_market_id"])
  return market_ids


def deposit(session: ApiSession, index: int) -> None:
  session.post(
    "/api/v1/wallet/test-deposit",
    headers={"Idempotency-Key": f"persistent-sim-deposit-{index:02d}"},
    json={"amount_minor": 100_000, "currency": "INR"},
  )


def place_order(
  session: ApiSession,
  *,
  market_id: str,
  outcome: str,
  price: int,
  quantity: int,
  key: str | None,
  expected: set[int] | None = None,
) -> httpx.Response:
  headers = {"Idempotency-Key": key} if key else {}
  return session.post(
    "/api/v1/orders",
    expected=expected or {201},
    headers=headers,
    json={
      "market_id": market_id,
      "outcome": outcome,
      "side": "BUY",
      "price_minor": price,
      "quantity": quantity,
    },
  )


def create_trading_day(users: dict[str, ApiSession], market_ids: list[str]) -> dict[str, int]:
  for index, email in enumerate(USER_EMAILS, start=1):
    deposit(users[email], index)

  for index in range(36):
    market_id = market_ids[index % len(market_ids)]
    yes_user = users[USER_EMAILS[index % len(USER_EMAILS)]]
    no_user = users[USER_EMAILS[(index + 1) % len(USER_EMAILS)]]
    quantity = 2 + (index % 3)
    yes_price = 40 + (index % 10)
    no_price = 100 - yes_price
    place_order(
      yes_user,
      market_id=market_id,
      outcome="YES",
      price=yes_price,
      quantity=quantity,
      key=f"persistent-sim-match-{index:02d}-yes",
    )
    place_order(
      no_user,
      market_id=market_id,
      outcome="NO",
      price=no_price,
      quantity=quantity,
      key=f"persistent-sim-match-{index:02d}-no",
    )

  partial_resting = place_order(
    users[USER_EMAILS[0]],
    market_id=market_ids[1],
    outcome="YES",
    price=45,
    quantity=10,
    key="persistent-sim-partial-yes",
  ).json()
  place_order(
    users[USER_EMAILS[1]],
    market_id=market_ids[1],
    outcome="NO",
    price=55,
    quantity=4,
    key="persistent-sim-partial-no",
  )

  unmatched = place_order(
    users[USER_EMAILS[2]],
    market_id=market_ids[2],
    outcome="YES",
    price=25,
    quantity=8,
    key="persistent-sim-unmatched",
  ).json()
  if unmatched["status"] in {"OPEN", "PARTIALLY_FILLED"}:
    users[USER_EMAILS[2]].post(f"/api/v1/orders/{unmatched['id']}/cancel")

  return {"partial_order_id": partial_resting["id"], "cancelled_order_id": unmatched["id"]}


def settle_first_market(admin: ApiSession, checker: ApiSession, public: ApiSession, market_id: str) -> None:
  detail = public.get(f"/api/v1/markets/{market_id}").json()
  if detail["status"] == "RESOLVED":
    return
  admin.post(f"/api/v1/admin/markets/{market_id}/close")
  admin.post(
    f"/api/v1/admin/markets/{market_id}/evidence",
    expected={201},
    json={
      "source_name": "Persistent simulation official source",
      "source_url": "https://example.com/pred-market-simulation/result",
      "captured_payload": {"winner": "YES", "simulation": True},
    },
  )
  detail = public.get(f"/api/v1/markets/{market_id}").json()
  yes_outcome_id = next(item["id"] for item in detail["outcomes"] if item["label"] == "YES")
  proposal = admin.post(
    f"/api/v1/admin/markets/{market_id}/resolution-proposals",
    expected={201},
    json={
      "result": "RESOLVE",
      "winning_outcome_id": yes_outcome_id,
      "reason": "Persistent simulation evidence resolves this market to YES.",
    },
  ).json()
  checker.post(f"/api/v1/admin/resolution-proposals/{proposal['id']}/approve")
  admin.post(
    f"/api/v1/admin/markets/{market_id}/settle",
    headers={"Idempotency-Key": "persistent-sim-settlement-1"},
  )


def expect_status(response: httpx.Response, expected: int, label: str) -> None:
  if response.status_code != expected:
    raise SimulationFailure(f"{label}: expected {expected}, received {response.status_code}: {response.text}")


def unlisted_draft_snapshot(question: str) -> dict[str, Any] | None:
  with SessionLocal() as db:
    draft = db.scalar(
      select(MarketDraft).where(
        MarketDraft.question == question,
        MarketDraft.listed_market_id.is_(None),
      )
    )
    if not draft:
      return None
    return {
      "status": draft.status,
      "listed_market_id": draft.listed_market_id,
      "checks": draft.checks_json,
    }


def run_negative_checks(
  base_url: str,
  admin: ApiSession,
  trader: ApiSession,
  other_user: ApiSession,
  market_ids: list[str],
) -> dict[str, int]:
  checks = 0
  unauthenticated = ApiSession(base_url)
  try:
    response = place_order(
      unauthenticated,
      market_id=market_ids[1],
      outcome="YES",
      price=22,
      quantity=1,
      key="persistent-negative-unauthenticated",
      expected={401},
    )
    expect_status(response, 401, "unauthenticated order")
    checks += 1
  finally:
    unauthenticated.close()

  source = settlement_source(admin, "sports")
  forbidden = trader.post(
    "/api/v1/admin/market-drafts",
    expected={403},
    json={
      "origin": "ADMIN",
      "category_slug": "sports",
      "market_type": "Binary",
      "question": "Will a normal user create a persistent admin-only market?",
      "outcomes": ["YES", "NO"],
      "close_time": "Dec 31, 2027 23:59 UTC",
      "source": source["name"],
      "resolution_rule": "YES resolves if the approved source confirms the persistent simulation event.",
      "settlement_source_id": source["id"],
    },
  )
  expect_status(forbidden, 403, "normal user admin draft")
  checks += 1

  duplicate_question = MARKET_SPECS[1].question
  duplicate_snapshot = unlisted_draft_snapshot(duplicate_question)
  if not duplicate_snapshot:
    duplicate = admin.post(
      "/api/v1/admin/market-drafts",
      expected={201},
      json={
        "origin": "ADMIN",
        "category_slug": "sports",
        "subcategory": "Persistent negative testing",
        "market_type": "Binary",
        "question": duplicate_question,
        "outcomes": ["YES", "NO"],
        "close_time": "Dec 31, 2027 23:59 UTC",
        "source": source["name"],
        "resolution_rule": "YES resolves if the approved source confirms the duplicate test event.",
        "void_policy": "Void only if the approved source is unavailable.",
        "settlement_source_id": source["id"],
        "discovery_source_id": source["id"],
        "admin_notes": "Persistent negative duplicate check.",
      },
    ).json()
    duplicate_snapshot = {
      "status": duplicate["status"],
      "listed_market_id": duplicate["listed_market_id"],
      "checks": duplicate["checks"],
    }
  if duplicate_snapshot["status"] != "NEEDS_CHANGES" or duplicate_snapshot["checks"]["duplicate_title"]["passed"] is not False:
    raise SimulationFailure(f"Duplicate market check failed: {duplicate_snapshot}")
  checks += 1

  no_source_question = "Will a persistent draft without an approved settlement source be listed?"
  no_source_snapshot = unlisted_draft_snapshot(no_source_question)
  if not no_source_snapshot:
    no_source = admin.post(
      "/api/v1/admin/market-drafts",
      expected={201},
      json={
        "origin": "ADMIN",
        "category_slug": "sports",
        "subcategory": "Persistent negative testing",
        "market_type": "Binary",
        "question": no_source_question,
        "outcomes": ["YES", "NO"],
        "close_time": "Dec 31, 2027 23:59 UTC",
        "source": "Unapproved persistent simulation source",
        "resolution_rule": "YES resolves if the unapproved source confirms the event.",
        "void_policy": "Void only if the source is unavailable.",
      },
    ).json()
    no_source_snapshot = {
      "status": no_source["status"],
      "listed_market_id": no_source["listed_market_id"],
      "checks": no_source["checks"],
    }
  if no_source_snapshot["status"] != "NEEDS_CHANGES" or no_source_snapshot["listed_market_id"] is not None:
    raise SimulationFailure(f"Unapproved source draft check failed: {no_source_snapshot}")
  no_source_drafts = admin.get("/api/v1/admin/market-drafts", params={"limit": 250}).json()["items"]
  no_source_draft = next(item for item in no_source_drafts if item["question"] == no_source_question and not item["listed_market_id"])
  blocked_approval = admin.post(f"/api/v1/admin/market-drafts/{no_source_draft['id']}/approve", expected={422})
  expect_status(blocked_approval, 422, "unapproved settlement source")
  checks += 1

  for label, price, quantity in [
    ("price zero", 0, 1),
    ("price one hundred", 100, 1),
    ("quantity zero", 40, 0),
  ]:
    response = place_order(
      trader,
      market_id=market_ids[1],
      outcome="YES",
      price=price,
      quantity=quantity,
      key=f"persistent-negative-{label.replace(' ', '-')}",
      expected={422},
    )
    expect_status(response, 422, label)
    checks += 1

  insufficient = place_order(
    trader,
    market_id=market_ids[1],
    outcome="YES",
    price=99,
    quantity=100_000,
    key="persistent-negative-insufficient",
    expected={402},
  )
  expect_status(insufficient, 402, "insufficient funds")
  checks += 1

  owner_order = place_order(
    trader,
    market_id=market_ids[1],
    outcome="YES",
    price=17,
    quantity=3,
    key="persistent-negative-owner-order",
  ).json()
  if owner_order["status"] in {"OPEN", "PARTIALLY_FILLED"}:
    non_owner = other_user.post(f"/api/v1/orders/{owner_order['id']}/cancel", expected={403})
    expect_status(non_owner, 403, "non-owner cancellation")
    checks += 1

  self_yes = place_order(
    trader,
    market_id=market_ids[2],
    outcome="YES",
    price=13,
    quantity=5,
    key="persistent-negative-self-yes",
  ).json()
  self_no = place_order(
    trader,
    market_id=market_ids[2],
    outcome="NO",
    price=87,
    quantity=5,
    key="persistent-negative-self-no",
  ).json()
  if self_yes["status"] != "OPEN" or self_no["status"] != "OPEN":
    raise SimulationFailure("Self-trade prevention failed: complementary orders did not both remain open.")
  checks += 1

  first = place_order(
    trader,
    market_id=market_ids[4],
    outcome="YES",
    price=31,
    quantity=2,
    key="persistent-negative-idempotent",
  ).json()
  second = place_order(
    trader,
    market_id=market_ids[4],
    outcome="YES",
    price=31,
    quantity=2,
    key="persistent-negative-idempotent",
  ).json()
  if first["id"] != second["id"]:
    raise SimulationFailure("Idempotency check failed: duplicate request created another order.")
  checks += 1

  missing_key = place_order(
    trader,
    market_id=market_ids[4],
    outcome="YES",
    price=23,
    quantity=1,
    key=None,
    expected={400},
  )
  expect_status(missing_key, 400, "missing idempotency key")
  checks += 1

  closed = place_order(
    trader,
    market_id=market_ids[0],
    outcome="YES",
    price=40,
    quantity=1,
    key="persistent-negative-closed-market",
    expected={422},
  )
  expect_status(closed, 422, "closed market order")
  checks += 1

  suggestion_question = "Will the persistent trader suggestion remain unlisted until admin approval?"
  suggestion_snapshot = unlisted_draft_snapshot(suggestion_question)
  if not suggestion_snapshot:
    suggestion = trader.post(
      "/api/v1/market-suggestions",
      expected={201},
      json={
        "category_slug": "weather-climate",
        "market_type": "Binary",
        "question": suggestion_question,
        "outcomes": ["YES", "NO"],
        "source": "Official persistent weather station report",
        "resolution_rule": "YES resolves if the official station confirms the persistent event.",
      },
    ).json()
    if not suggestion["draft_id"]:
      raise SimulationFailure("Trader suggestion did not create a market draft.")
    suggestion_snapshot = unlisted_draft_snapshot(suggestion_question)
  if not suggestion_snapshot or suggestion_snapshot["listed_market_id"] is not None:
    raise SimulationFailure(f"Trader suggestion listed without admin approval: {suggestion_snapshot}")
  checks += 1
  return {"negative_checks": checks}


def verify_database(market_ids: list[str]) -> dict[str, int]:
  with SessionLocal() as db:
    user_count = db.scalar(select(func.count(User.id)).where(User.email.in_(USER_EMAILS))) or 0
    market_count = db.scalar(select(func.count(Market.id)).where(Market.id.in_(market_ids))) or 0
    order_count = db.scalar(select(func.count(Order.id)).where(Order.idempotency_key.like("persistent-sim-%"))) or 0
    negative_order_count = db.scalar(select(func.count(Order.id)).where(Order.idempotency_key.like("persistent-negative-%"))) or 0
    trade_count = db.scalar(select(func.count(Trade.id)).where(Trade.market_id.in_(market_ids))) or 0
    position_count = db.scalar(select(func.count(Position.id)).where(Position.market_id.in_(market_ids))) or 0
    wallet_count = db.scalar(
      select(func.count(Wallet.id)).join(User, Wallet.user_id == User.id).where(User.email.in_(USER_EMAILS))
    ) or 0
    settlement_count = db.scalar(select(func.count(Settlement.id)).where(Settlement.market_id.in_(market_ids))) or 0
    audit_count = db.scalar(
      select(func.count(AuditLog.id)).where(
        AuditLog.event_type.in_(["MARKET_DRAFT_LISTED", "ORDER_CREATED", "ORDER_CANCELLED", "MARKET_SETTLED"])
      )
    ) or 0
    realtime_count = db.scalar(select(func.count(RealtimeEvent.id)).where(RealtimeEvent.market_id.in_(market_ids))) or 0
    debit_total = int(db.scalar(select(func.coalesce(func.sum(LedgerEntry.amount_minor), 0)).where(LedgerEntry.side == "DEBIT")) or 0)
    credit_total = int(db.scalar(select(func.coalesce(func.sum(LedgerEntry.amount_minor), 0)).where(LedgerEntry.side == "CREDIT")) or 0)

    expected = {
      "users": 20,
      "markets": 6,
      "orders": 75,
      "trades_minimum": 37,
      "positions_minimum": 40,
      "wallets": 20,
      "settlements": 1,
    }
    actual = {
      "users": user_count,
      "markets": market_count,
      "orders": order_count,
      "negative_orders": negative_order_count,
      "trades": trade_count,
      "positions": position_count,
      "wallets": wallet_count,
      "settlements": settlement_count,
      "audit_events": audit_count,
      "realtime_events": realtime_count,
      "ledger_debits": debit_total,
      "ledger_credits": credit_total,
    }
    failures = []
    for key in ["users", "markets", "orders", "wallets", "settlements"]:
      if actual[key] != expected[key]:
        failures.append(f"{key}: expected {expected[key]}, got {actual[key]}")
    if trade_count < expected["trades_minimum"]:
      failures.append(f"trades: expected at least {expected['trades_minimum']}, got {trade_count}")
    if position_count < expected["positions_minimum"]:
      failures.append(f"positions: expected at least {expected['positions_minimum']}, got {position_count}")
    if debit_total != credit_total:
      failures.append(f"ledger is unbalanced: debits={debit_total}, credits={credit_total}")
    if failures:
      raise SimulationFailure("Persistent database verification failed: " + "; ".join(failures))
    return actual


def run(base_url: str = DEFAULT_API_BASE_URL) -> dict[str, Any]:
  if settings.environment.lower() not in {"development", "local", "test"}:
    raise SimulationFailure("Persistent simulation is disabled outside development/local/test environments.")
  if not settings.database_url.startswith("postgresql"):
    raise SimulationFailure("Persistent simulation requires the local PostgreSQL database.")

  public = ApiSession(base_url)
  sessions: list[ApiSession] = [public]
  try:
    health = public.get("/api/v1/health").json()
    if health.get("database") != "ok" or health.get("redis") != "ok":
      raise SimulationFailure(f"Backend dependencies are not healthy: {health}")

    admin = authenticate(base_url, "admin@predmarket.dev")
    checker = authenticate(base_url, "checker@predmarket.dev")
    trader = authenticate(base_url, "trader@predmarket.dev")
    sessions.extend([admin, checker, trader])

    users = {email: authenticate(base_url, email, create=True) for email in USER_EMAILS}
    sessions.extend(users.values())
    other_user = users[USER_EMAILS[-1]]
    market_ids = create_markets(admin, public)
    trading_state = create_trading_day(users, market_ids)

    order_book = public.get(f"/api/v1/markets/{market_ids[1]}/order-book").json()["order_book"]
    detail = public.get(f"/api/v1/markets/{market_ids[1]}").json()
    if not order_book["yes_bids"]:
      raise SimulationFailure("Order book verification failed: no resting YES bids are visible.")
    if not detail["recent_trades"]:
      raise SimulationFailure("Recent-trades verification failed: no trades are visible through the market API.")

    settle_first_market(admin, checker, public, market_ids[0])
    negative = run_negative_checks(base_url, admin, trader, other_user, market_ids)
    admin.post("/api/v1/admin/analytics/recompute")
    database = verify_database(market_ids)
    return {
      "status": "complete",
      "api_base_url": base_url,
      "database": settings.database_url.rsplit("@", 1)[-1],
      "market_ids": market_ids,
      "trading_state": trading_state,
      **negative,
      **database,
    }
  finally:
    for session in sessions:
      session.close()


def main() -> None:
  base_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_API_BASE_URL
  print(json.dumps(run(base_url), indent=2, sort_keys=True))


if __name__ == "__main__":
  main()
