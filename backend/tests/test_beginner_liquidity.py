from sqlalchemy import select

from app.modules.market_maker.service import get_or_create_market_maker, replenish_market_liquidity
from app.modules.markets.models import Market
from app.modules.markets.service import computed_order_book, order_book_snapshot
from app.modules.orders.models import Order
from app.modules.wallets.models import Wallet
from conftest import sign_in


def test_seeded_json_is_not_served_as_live_depth(client, db_session):
  market = db_session.get(Market, "ind-aus-final")
  assert market.order_book_json

  response = client.get("/api/v1/markets/ind-aus-final/order-book")

  assert response.status_code == 200
  assert response.json()["order_book"] == {"yes_bids": [], "no_bids": []}
  assert response.json()["quote"]["yes_ask"] is None


def test_market_maker_depth_is_executable_and_idempotent(db_session):
  created = replenish_market_liquidity(db_session, "ind-aus-final", force=True)
  first = order_book_snapshot(db_session, db_session.get(Market, "ind-aus-final"))
  repeated = replenish_market_liquidity(db_session, "ind-aus-final", force=True)
  maker = get_or_create_market_maker(db_session)
  wallet = db_session.scalar(select(Wallet).where(Wallet.user_id == maker.id))

  assert created == 10
  assert repeated == 0
  assert [level["quantity"] for level in first["order_book"]["yes_bids"][:5]] == [200, 160, 120, 80, 40]
  assert [level["quantity"] for level in first["order_book"]["no_bids"][:5]] == [200, 160, 120, 80, 40]
  assert first["quote"]["spread"] == 2
  assert maker.is_system is True
  assert wallet and wallet.available_balance_minor + wallet.locked_balance_minor == 10_000_000


def test_quick_buy_fills_against_maker_and_updates_ticker(client, db_session):
  replenish_market_liquidity(db_session, "ind-aus-final", force=True)
  db_session.commit()
  before = client.get("/api/v1/markets/ind-aus-final").json()
  yes = next(outcome for outcome in before["outcomes"] if outcome["label"] == "YES")
  ask = before["quote"]["yes_ask"]

  sign_in(client)
  assert client.post(
    "/api/v1/wallet/test-deposit",
    json={"amount_minor": 50_000},
    headers={"Idempotency-Key": "beginner-liquidity-deposit"},
  ).status_code == 200
  response = client.post(
    "/api/v1/orders",
    json={
      "market_id": "ind-aus-final",
      "outcome_id": yes["id"],
      "side": "BUY",
      "price_minor": ask,
      "quantity": 5,
    },
    headers={"Idempotency-Key": "beginner-liquidity-order"},
  )

  assert response.status_code == 201
  assert response.json()["status"] == "FILLED"
  assert response.json()["filled_quantity"] == 5
  after = client.get("/api/v1/markets/ind-aus-final").json()
  assert after["probability"] == ask
  assert after["volume_24h"] > before["volume_24h"]
  assert after["price_history"][-1]["value"] == ask


def test_public_order_book_is_aggregated_and_anonymous(db_session):
  replenish_market_liquidity(db_session, "ind-aus-final", force=True)
  market = db_session.get(Market, "ind-aus-final")
  book = computed_order_book(db_session, market)
  serialized = str(book).lower()

  assert "user" not in serialized
  assert "order_id" not in serialized
  assert len(db_session.scalars(select(Order).where(Order.market_id == market.id)).all()) == 10
