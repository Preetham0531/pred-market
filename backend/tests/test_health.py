def test_root_health(client):
  response = client.get("/health")

  assert response.status_code == 200
  assert response.json()["status"] == "ok"


def test_liveness_is_process_only(client):
  response = client.get("/health/live")

  assert response.status_code == 200
  assert response.json()["status"] == "ok"


def test_readiness_reports_dependencies(client):
  response = client.get("/health/ready")

  assert response.status_code in {200, 503}
  assert response.json()["database"] in {"ok", "error"}
  assert response.json()["redis"] in {"ok", "error"}


def test_version(client):
  response = client.get("/api/v1/version")

  assert response.status_code == 200
  assert response.json()["api_prefix"] == "/api/v1"
