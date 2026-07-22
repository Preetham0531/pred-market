import time

import pyotp
from sqlalchemy import select

from app.core.config import settings
from app.modules.audit.models import AuditLog
from app.modules.auth.models import MfaRecoveryCode, UserMfaFactor


def _enroll(client, *, email: str = "admin@predmarket.dev") -> tuple[str, list[str]]:
  signed_in = client.post("/api/v1/auth/sign-in", json={"email": email, "password": "StrongPass123"})
  assert signed_in.status_code == 200
  setup = client.post("/api/v1/auth/mfa/totp/setup")
  assert setup.status_code == 200
  payload = setup.json()
  code = pyotp.TOTP(payload["secret"]).now()
  confirmed = client.post("/api/v1/auth/mfa/totp/confirm", json={"code": code})
  assert confirmed.status_code == 200
  return payload["secret"], confirmed.json()["recovery_codes"]


def test_admin_mfa_enrollment_challenge_and_replay_protection(client, db_session, monkeypatch):
  monkeypatch.setattr(settings, "admin_mfa_required", True)
  secret, recovery_codes = _enroll(client)

  status = client.get("/api/v1/auth/mfa/status")
  assert status.status_code == 200
  assert status.json() == {
    "enrolled": True,
    "required": True,
    "verified_for_session": True,
    "factor_id": status.json()["factor_id"],
    "recovery_codes_remaining": 10,
  }
  assert len(recovery_codes) == 10
  assert db_session.scalars(select(MfaRecoveryCode)).all()

  assert client.post("/api/v1/auth/sign-out").status_code == 200
  password_step = client.post("/api/v1/auth/sign-in", json={"email": "admin@predmarket.dev", "password": "StrongPass123"})
  assert password_step.status_code == 202
  assert password_step.json()["mfa_required"] is True
  assert not password_step.cookies.get("pred_market_v1_access_token")

  next_code = pyotp.TOTP(secret).at(time.time() + 30)
  verified = client.post("/api/v1/auth/mfa/challenge/verify", json={"code": next_code})
  assert verified.status_code == 200
  assert client.get("/api/v1/admin/markets/review").status_code == 200

  assert client.post("/api/v1/auth/sign-out").status_code == 200
  assert client.post("/api/v1/auth/sign-in", json={"email": "admin@predmarket.dev", "password": "StrongPass123"}).status_code == 202
  replayed = client.post("/api/v1/auth/mfa/challenge/verify", json={"code": next_code})
  assert replayed.status_code == 422
  assert replayed.json()["error"]["code"] == "MFA_CODE_REPLAYED"
  assert db_session.scalar(select(AuditLog).where(AuditLog.event_type == "MFA_ENROLLED")) is not None


def test_recovery_code_is_one_time(client, monkeypatch):
  monkeypatch.setattr(settings, "admin_mfa_required", True)
  _, recovery_codes = _enroll(client)
  recovery_code = recovery_codes[0]

  assert client.post("/api/v1/auth/sign-out").status_code == 200
  assert client.post("/api/v1/auth/sign-in", json={"email": "admin@predmarket.dev", "password": "StrongPass123"}).status_code == 202
  recovered = client.post("/api/v1/auth/mfa/challenge/verify", json={"code": recovery_code})
  assert recovered.status_code == 200

  assert client.post("/api/v1/auth/sign-out").status_code == 200
  assert client.post("/api/v1/auth/sign-in", json={"email": "admin@predmarket.dev", "password": "StrongPass123"}).status_code == 202
  reused = client.post("/api/v1/auth/mfa/challenge/verify", json={"code": recovery_code})
  assert reused.status_code == 422
  assert reused.json()["error"]["code"] == "MFA_CODE_INVALID"


def test_admin_session_without_enrollment_is_restricted(client, monkeypatch):
  monkeypatch.setattr(settings, "admin_mfa_required", True)
  signed_in = client.post("/api/v1/auth/sign-in", json={"email": "admin@predmarket.dev", "password": "StrongPass123"})
  assert signed_in.status_code == 200
  assert signed_in.json()["mfa_setup_required"] is True
  assert client.get("/api/v1/auth/mfa/status").status_code == 200

  blocked = client.get("/api/v1/admin/markets/review")
  assert blocked.status_code == 403
  assert blocked.json()["error"]["code"] == "MFA_REQUIRED"


def test_admin_factor_cannot_be_removed_while_required(client, db_session, monkeypatch):
  monkeypatch.setattr(settings, "admin_mfa_required", True)
  secret, _ = _enroll(client)
  factor = db_session.scalar(select(UserMfaFactor).where(UserMfaFactor.confirmed_at.is_not(None)))
  assert factor is not None

  response = client.request(
    "DELETE",
    f"/api/v1/auth/mfa/factors/{factor.id}",
    json={"code": pyotp.TOTP(secret).at(time.time() + 30)},
  )
  assert response.status_code == 409
  assert response.json()["error"]["code"] == "ADMIN_MFA_REQUIRED"
