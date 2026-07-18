def test_seeded_markets_are_publicly_readable(client):
  response = client.get("/api/v1/markets")

  assert response.status_code == 200
  body = response.json()
  assert len(body["items"]) >= 5
  assert body["items"][0]["outcomes"]


def test_market_filters_and_detail(client):
  filtered = client.get("/api/v1/markets", params={"category": "sports", "status": "OPEN"})
  assert filtered.status_code == 200
  assert all(item["category_slug"] == "sports" for item in filtered.json()["items"])

  detail = client.get("/api/v1/markets/ind-aus-final")
  assert detail.status_code == 200
  assert detail.json()["id"] == "ind-aus-final"
  assert detail.json()["price_history"]

  order_book = client.get("/api/v1/markets/ind-aus-final/order-book")
  assert order_book.status_code == 200
  assert "yes_bids" in order_book.json()["order_book"]

  price_history = client.get("/api/v1/markets/ind-aus-final/price-history")
  assert price_history.status_code == 200
  assert price_history.json()["points"]


def test_category_read(client):
  response = client.get("/api/v1/categories/sports")

  assert response.status_code == 200
  assert response.json()["slug"] == "sports"
