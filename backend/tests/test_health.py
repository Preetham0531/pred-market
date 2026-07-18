def test_root_health(client):
  response = client.get("/health")

  assert response.status_code == 200
  assert response.json()["status"] == "ok"


def test_version(client):
  response = client.get("/api/v1/version")

  assert response.status_code == 200
  assert response.json()["api_prefix"] == "/api/v1"
