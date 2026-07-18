from sqlalchemy import select

from app.modules.audit.models import AuditLog
from app.modules.auth.models import AdminImpersonationSession
from app.modules.users.models import User


def test_sign_up_creates_user_session_and_audit(client, db_session):
  response = client.post(
    "/api/v1/auth/sign-up",
    json={
      "email": "new@predmarket.dev",
      "password": "StrongPass123",
      "display_name": "New Trader",
      "terms_acceptance": True,
    },
  )

  assert response.status_code == 201
  assert response.json()["user"]["email"] == "new@predmarket.dev"
  assert response.cookies.get("pred_market_v1_refresh_token")
  user = db_session.scalar(select(User).where(User.email == "new@predmarket.dev"))
  assert user is not None
  assert {role.role for role in user.roles} == {"USER"}
  assert db_session.scalar(select(AuditLog).where(AuditLog.event_type == "USER_SIGNED_UP")) is not None


def test_duplicate_email_rejected(client):
  response = client.post(
    "/api/v1/auth/sign-up",
    json={"email": "trader@predmarket.dev", "password": "StrongPass123", "terms_acceptance": True},
  )

  assert response.status_code == 409
  assert response.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_weak_password_rejected(client):
  response = client.post(
    "/api/v1/auth/sign-up",
    json={"email": "weak@predmarket.dev", "password": "short", "terms_acceptance": True},
  )

  assert response.status_code == 422


def test_sign_in_me_refresh_and_sign_out(client):
  sign_in = client.post("/api/v1/auth/sign-in", json={"email": "trader@predmarket.dev", "password": "StrongPass123"})
  assert sign_in.status_code == 200

  me = client.get("/api/v1/auth/me")
  assert me.status_code == 200
  assert me.json()["user"]["email"] == "trader@predmarket.dev"
  assert me.json()["actor"]["email"] == "trader@predmarket.dev"
  assert me.json()["impersonation"] is None
  assert sign_in.cookies.get("pred_market_v1_access_token")
  assert sign_in.cookies.get("pred_market_v1_refresh_token")
  assert sign_in.cookies.get("pred_market_v1_csrf_token")

  refresh = client.post("/api/v1/auth/refresh")
  assert refresh.status_code == 200
  assert refresh.cookies.get("pred_market_v1_refresh_token")

  sign_out = client.post("/api/v1/auth/sign-out")
  assert sign_out.status_code == 200
  assert client.get("/api/v1/auth/me").status_code == 401


def test_bad_credentials_are_generic(client):
  response = client.post("/api/v1/auth/sign-in", json={"email": "trader@predmarket.dev", "password": "WrongPass123"})

  assert response.status_code == 401
  assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"
  assert response.json()["error"]["message"] == "Invalid email or password."


def test_non_admin_cannot_access_admin_dependency(client):
  response = client.post("/api/v1/auth/sign-in", json={"email": "trader@predmarket.dev", "password": "StrongPass123"})
  assert response.status_code == 200

  admin_response = client.get("/api/v1/admin/markets/review")
  assert admin_response.status_code == 403


def test_mutating_authenticated_request_requires_csrf(client):
  response = client.post("/api/v1/auth/sign-in", json={"email": "trader@predmarket.dev", "password": "StrongPass123"})
  assert response.status_code == 200

  blocked = client.post("/api/v1/wallet/test-deposit", json={"amount_minor": 1000}, headers={"X-CSRF-Token": ""})
  assert blocked.status_code == 403
  assert blocked.json()["error"]["code"] == "CSRF_TOKEN_INVALID"


def test_auth_rate_limit_returns_429(client):
  for _ in range(3):
    assert client.post("/api/v1/auth/password-reset/request", json={"email": "trader@predmarket.dev"}).status_code == 200

  limited = client.post("/api/v1/auth/password-reset/request", json={"email": "trader@predmarket.dev"})
  assert limited.status_code == 429
  assert limited.json()["error"]["code"] == "RATE_LIMITED"


def test_admin_can_start_and_stop_read_only_impersonation(client, db_session):
  response = client.post("/api/v1/auth/sign-in", json={"email": "admin@predmarket.dev", "password": "StrongPass123"})
  assert response.status_code == 200
  trader = db_session.scalar(select(User).where(User.email == "trader@predmarket.dev"))

  started = client.post(
    "/api/v1/admin/impersonation/start",
    json={"target_user_id": trader.id, "reason": "Support review"},
  )
  assert started.status_code == 200
  assert started.json()["user"]["email"] == "trader@predmarket.dev"
  assert started.json()["actor"]["email"] == "admin@predmarket.dev"
  assert started.json()["impersonation"]["mode"] == "READ_ONLY"
  assert db_session.scalar(select(AdminImpersonationSession).where(AdminImpersonationSession.target_user_id == trader.id)) is not None

  blocked_order = client.post(
    "/api/v1/orders",
    json={"market_id": "ind-aus-final", "outcome": "YES", "side": "BUY", "price_minor": 40, "quantity": 1},
    headers={"Idempotency-Key": "imp-blocked"},
  )
  assert blocked_order.status_code == 403
  assert blocked_order.json()["error"]["code"] == "IMPERSONATION_READ_ONLY"

  stopped = client.post("/api/v1/admin/impersonation/stop")
  assert stopped.status_code == 200
  assert stopped.json()["user"]["email"] == "admin@predmarket.dev"
  assert stopped.json()["impersonation"] is None


def test_admin_cannot_impersonate_admin(client, db_session):
  response = client.post("/api/v1/auth/sign-in", json={"email": "admin@predmarket.dev", "password": "StrongPass123"})
  assert response.status_code == 200
  checker = db_session.scalar(select(User).where(User.email == "checker@predmarket.dev"))

  blocked = client.post(
    "/api/v1/admin/impersonation/start",
    json={"target_user_id": checker.id, "reason": "Invalid admin switch"},
  )
  assert blocked.status_code == 403
  assert blocked.json()["error"]["code"] == "ADMIN_IMPERSONATION_FORBIDDEN"
  assert db_session.scalar(select(AuditLog).where(AuditLog.event_type == "ADMIN_IMPERSONATION_DENIED")) is not None
