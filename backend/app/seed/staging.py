from copy import deepcopy

from sqlalchemy import select

from app.db.session import SessionLocal
from app.modules.audit.service import write_audit_log
from app.modules.market_issuance.models import DataSource
from app.modules.markets.models import Category, Market, MarketRule, Outcome
from app.seed.dev import CATEGORIES, DATA_SOURCES, MARKETS

EXTRA_MARKET = {
  "id": "policy-rate-hold-simulated",
  "title": "Simulation: Will the next policy rate decision be a hold?",
  "category_slug": "economics",
  "subcategory": "Rates",
  "market_type": "Binary",
  "status": "OPEN",
  "close_time": "Dec 31, 2026 12:00 UTC",
  "source": "Simulated approved central bank release",
  "rule_summary": "YES resolves if the simulated official decision records no policy-rate change.",
  "probability": 58,
  "change_24h": 1.2,
  "volume_24h": 0,
  "total_volume": 0,
  "liquidity": 0,
  "spread": 4.0,
  "traders": 0,
  "risk_notes_json": ["Staging simulation only.", "A real listing requires an approved official settlement source."],
  "price_history_json": [],
  "order_book_json": {},
  "recent_trades_json": [],
  "outcomes": [{"label": "YES", "price": 58, "probability": 58}, {"label": "NO", "price": 42, "probability": 42}],
}


def _seed_categories(db) -> int:
  for payload in CATEGORIES:
    existing = db.get(Category, payload["slug"])
    if existing:
      for key, value in payload.items():
        setattr(existing, key, value)
    else:
      db.add(Category(**deepcopy(payload)))
  db.flush()
  return len(CATEGORIES)


def _seed_sources(db) -> int:
  for payload in DATA_SOURCES:
    existing = db.scalar(select(DataSource).where(DataSource.name == payload["name"], DataSource.provider == payload["provider"]))
    if existing:
      for key, value in payload.items():
        setattr(existing, key, deepcopy(value))
    else:
      db.add(DataSource(**deepcopy(payload)))
  db.flush()
  return len(DATA_SOURCES)


def _market_payloads() -> list[dict]:
  items = []
  for source in MARKETS:
    payload = deepcopy(source)
    if not payload["title"].startswith("Simulation:"):
      payload["title"] = f"Simulation: {payload['title']}"
    payload["risk_notes_json"] = ["Staging simulation only.", *payload.get("risk_notes_json", [])]
    items.append(payload)
  items.append(deepcopy(EXTRA_MARKET))
  return items


def _seed_markets(db) -> int:
  payloads = _market_payloads()
  for source in payloads:
    payload = deepcopy(source)
    outcomes = payload.pop("outcomes")
    market = db.get(Market, payload["id"])
    if market:
      for key, value in payload.items():
        setattr(market, key, value)
    else:
      market = Market(**payload)
      db.add(market)
      db.flush()
    rule = db.scalar(select(MarketRule).where(MarketRule.market_id == market.id))
    if rule is None:
      db.add(
        MarketRule(
          market_id=market.id,
          resolution_rule=market.rule_summary,
          void_policy="Void if the simulated source is unavailable or the event is cancelled.",
          source_url=None,
        )
      )
    else:
      rule.resolution_rule = market.rule_summary
      rule.void_policy = "Void if the simulated source is unavailable or the event is cancelled."
    existing_outcomes = {outcome.label: outcome for outcome in market.outcomes}
    for outcome_payload in outcomes:
      outcome = existing_outcomes.get(outcome_payload["label"])
      if outcome:
        outcome.price = outcome_payload["price"]
        outcome.probability = outcome_payload["probability"]
      else:
        market.outcomes.append(Outcome(**outcome_payload))
  db.flush()
  return len(payloads)


def seed_staging_database(db) -> dict[str, int]:
  result = {
    "categories": _seed_categories(db),
    "sources": _seed_sources(db),
    "markets": _seed_markets(db),
  }
  write_audit_log(db, event_type="STAGING_REFERENCE_DATA_SEEDED", metadata=result)
  return result


def seed_staging_data() -> dict[str, int]:
  with SessionLocal() as db:
    result = seed_staging_database(db)
    db.commit()
    return result


def main() -> None:
  result = seed_staging_data()
  print(f"Staging seed complete: {result['categories']} categories, {result['sources']} sources, {result['markets']} markets.")


if __name__ == "__main__":
  main()
