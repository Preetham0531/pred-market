def test_user_can_add_list_and_remove_watchlist_market(client):
  assert client.post("/api/v1/auth/sign-in", json={"email": "trader@predmarket.dev", "password": "StrongPass123"}).status_code == 200

  add = client.post("/api/v1/watchlist/ind-aus-final")
  assert add.status_code == 200
  assert add.json() == {"market_id": "ind-aus-final", "watchlisted": True}

  listed = client.get("/api/v1/watchlist")
  assert listed.status_code == 200
  assert [item["id"] for item in listed.json()["items"]] == ["ind-aus-final"]

  remove = client.delete("/api/v1/watchlist/ind-aus-final")
  assert remove.status_code == 200
  assert remove.json() == {"market_id": "ind-aus-final", "watchlisted": False}

  listed_again = client.get("/api/v1/watchlist")
  assert listed_again.status_code == 200
  assert listed_again.json()["items"] == []


def test_watchlist_requires_auth(client):
  assert client.get("/api/v1/watchlist").status_code == 401
