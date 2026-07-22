from __future__ import annotations

import base64
import hashlib
import secrets
import time
from dataclasses import dataclass
from hmac import compare_digest

import pyotp
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.core.security import hash_password, new_token, utc_now, verify_password
from app.db.redis import get_redis
from app.modules.audit.service import write_audit_log
from app.modules.auth.models import MfaRecoveryCode, UserMfaFactor
from app.modules.users.models import User

MFA_CHALLENGE_PREFIX = "mfa_challenge:"
_LOCAL_CHALLENGES: dict[str, dict[str, str]] = {}


@dataclass(frozen=True)
class VerifiedMfa:
  user: User
  method: str


def _fernet() -> Fernet:
  configured = settings.mfa_encryption_key.strip()
  if configured:
    try:
      return Fernet(configured.encode("ascii"))
    except (ValueError, TypeError) as exc:
      raise RuntimeError("MFA_ENCRYPTION_KEY must be a valid Fernet key.") from exc
  derived = hashlib.sha256(settings.jwt_secret_key.encode("utf-8")).digest()
  return Fernet(base64.urlsafe_b64encode(derived))


def encrypt_secret(secret: str) -> str:
  return _fernet().encrypt(secret.encode("ascii")).decode("ascii")


def decrypt_secret(ciphertext: str) -> str:
  try:
    return _fernet().decrypt(ciphertext.encode("ascii")).decode("ascii")
  except InvalidToken as exc:
    raise AppError(500, "MFA_SECRET_UNAVAILABLE", "Authenticator configuration cannot be decrypted.") from exc


def active_factor(db: Session, user_id: str) -> UserMfaFactor | None:
  return db.scalar(
    select(UserMfaFactor).where(
      UserMfaFactor.user_id == user_id,
      UserMfaFactor.confirmed_at.is_not(None),
      UserMfaFactor.disabled_at.is_(None),
    )
  )


def pending_factor(db: Session, user_id: str) -> UserMfaFactor | None:
  return db.scalar(
    select(UserMfaFactor).where(
      UserMfaFactor.user_id == user_id,
      UserMfaFactor.confirmed_at.is_(None),
      UserMfaFactor.disabled_at.is_(None),
    )
  )


def user_requires_mfa(db: Session, user: User, roles: list[str]) -> bool:
  return active_factor(db, user.id) is not None or (settings.admin_mfa_required and "ADMIN" in roles)


def mfa_status(db: Session, user: User, *, session_verified: bool) -> dict:
  factor = active_factor(db, user.id)
  remaining = 0
  if factor:
    remaining = db.scalar(
      select(func.count()).select_from(MfaRecoveryCode).where(
        MfaRecoveryCode.factor_id == factor.id,
        MfaRecoveryCode.used_at.is_(None),
      )
    ) or 0
  roles = {role.role for role in user.roles}
  return {
    "enrolled": factor is not None,
    "required": settings.admin_mfa_required and "ADMIN" in roles,
    "verified_for_session": session_verified,
    "factor_id": factor.id if factor else None,
    "recovery_codes_remaining": int(remaining),
  }


def create_challenge(user: User, *, request_id: str | None, user_agent: str | None) -> str:
  token = f"mfa_{new_token(32)}"
  payload = {
    "user_id": user.id,
    "attempts": "0",
    "request_id": request_id or "",
    "user_agent": user_agent or "",
  }
  try:
    redis = get_redis()
    redis.hset(f"{MFA_CHALLENGE_PREFIX}{token}", mapping=payload)
    redis.expire(f"{MFA_CHALLENGE_PREFIX}{token}", settings.mfa_challenge_ttl_seconds)
  except Exception:
    payload["expires_at"] = str(time.time() + settings.mfa_challenge_ttl_seconds)
    _LOCAL_CHALLENGES[token] = payload
  return token


def _load_challenge(token: str | None) -> dict[str, str] | None:
  if not token:
    return None
  try:
    return get_redis().hgetall(f"{MFA_CHALLENGE_PREFIX}{token}") or None
  except Exception:
    payload = _LOCAL_CHALLENGES.get(token)
    if payload and float(payload.get("expires_at", "0")) > time.time():
      return payload
    _LOCAL_CHALLENGES.pop(token, None)
    return None


def _save_attempt(token: str, payload: dict[str, str]) -> None:
  attempts = int(payload.get("attempts", "0")) + 1
  if attempts >= 5:
    consume_challenge(token)
    raise AppError(423, "MFA_CHALLENGE_LOCKED", "Too many invalid authenticator attempts. Sign in again.")
  payload["attempts"] = str(attempts)
  try:
    get_redis().hset(f"{MFA_CHALLENGE_PREFIX}{token}", mapping={"attempts": str(attempts)})
  except Exception:
    _LOCAL_CHALLENGES[token] = payload


def consume_challenge(token: str | None) -> None:
  if not token:
    return
  try:
    get_redis().delete(f"{MFA_CHALLENGE_PREFIX}{token}")
  except Exception:
    _LOCAL_CHALLENGES.pop(token, None)


def _verify_totp(factor: UserMfaFactor, code: str) -> bool:
  normalized = code.replace(" ", "").strip()
  if not normalized.isdigit() or len(normalized) != 6:
    return False
  totp = pyotp.TOTP(decrypt_secret(factor.secret_ciphertext))
  current_step = int(time.time()) // totp.interval
  for offset in (-1, 0, 1):
    step = current_step + offset
    if compare_digest(totp.at(step * totp.interval), normalized):
      if factor.last_used_step is not None and step <= factor.last_used_step:
        raise AppError(422, "MFA_CODE_REPLAYED", "That authenticator code has already been used.")
      factor.last_used_step = step
      return True
  return False


def _verify_recovery_code(db: Session, factor: UserMfaFactor, code: str) -> bool:
  normalized = code.strip().upper()
  for row in db.scalars(
    select(MfaRecoveryCode).where(MfaRecoveryCode.factor_id == factor.id, MfaRecoveryCode.used_at.is_(None))
  ).all():
    if verify_password(normalized, row.code_hash):
      row.used_at = utc_now()
      return True
  return False


def verify_challenge(db: Session, token: str | None, code: str) -> VerifiedMfa:
  payload = _load_challenge(token)
  if not payload:
    raise AppError(401, "MFA_CHALLENGE_EXPIRED", "The authenticator challenge expired. Sign in again.")
  user = db.get(User, payload["user_id"])
  factor = active_factor(db, payload["user_id"])
  if not user or not factor:
    consume_challenge(token)
    raise AppError(401, "MFA_CHALLENGE_INVALID", "The authenticator challenge is no longer valid.")
  method = "TOTP"
  valid = _verify_totp(factor, code)
  if not valid:
    method = "RECOVERY_CODE"
    valid = _verify_recovery_code(db, factor, code)
  if not valid:
    _save_attempt(token or "", payload)
    write_audit_log(db, event_type="MFA_CHALLENGE_FAILED", actor_user_id=user.id, target_user_id=user.id)
    raise AppError(422, "MFA_CODE_INVALID", "The authenticator or recovery code is invalid.")
  consume_challenge(token)
  write_audit_log(db, event_type="MFA_CHALLENGE_VERIFIED", actor_user_id=user.id, target_user_id=user.id, metadata={"method": method})
  return VerifiedMfa(user=user, method=method)


def begin_totp_setup(db: Session, user: User, *, request_id: str | None) -> dict:
  if active_factor(db, user.id):
    raise AppError(409, "MFA_ALREADY_ENROLLED", "An authenticator app is already configured.")
  existing = pending_factor(db, user.id)
  if existing:
    db.delete(existing)
    db.flush()
  secret = pyotp.random_base32()
  factor = UserMfaFactor(user_id=user.id, secret_ciphertext=encrypt_secret(secret))
  db.add(factor)
  db.flush()
  issuer = "Pred-Market"
  uri = pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name=issuer)
  write_audit_log(db, event_type="MFA_SETUP_STARTED", actor_user_id=user.id, target_user_id=user.id, request_id=request_id)
  return {"factor_id": factor.id, "secret": secret, "otpauth_uri": uri, "issuer": issuer, "account_name": user.email}


def _new_recovery_codes() -> list[str]:
  return [f"PM-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}" for _ in range(10)]


def replace_recovery_codes(db: Session, user: User, factor: UserMfaFactor) -> list[str]:
  db.execute(delete(MfaRecoveryCode).where(MfaRecoveryCode.factor_id == factor.id))
  codes = _new_recovery_codes()
  for code in codes:
    db.add(MfaRecoveryCode(user_id=user.id, factor_id=factor.id, code_hash=hash_password(code)))
  return codes


def confirm_totp_setup(db: Session, user: User, code: str, *, request_id: str | None) -> tuple[UserMfaFactor, list[str]]:
  factor = pending_factor(db, user.id)
  if not factor or not _verify_totp(factor, code):
    raise AppError(422, "MFA_CODE_INVALID", "The authenticator code is invalid.")
  factor.confirmed_at = utc_now()
  codes = replace_recovery_codes(db, user, factor)
  write_audit_log(db, event_type="MFA_ENROLLED", actor_user_id=user.id, target_user_id=user.id, request_id=request_id)
  return factor, codes


def regenerate_recovery_codes(db: Session, user: User, code: str, *, request_id: str | None) -> list[str]:
  factor = active_factor(db, user.id)
  if not factor or not _verify_totp(factor, code):
    raise AppError(422, "MFA_CODE_INVALID", "A current authenticator code is required.")
  codes = replace_recovery_codes(db, user, factor)
  write_audit_log(db, event_type="MFA_RECOVERY_CODES_REGENERATED", actor_user_id=user.id, target_user_id=user.id, request_id=request_id)
  return codes


def disable_factor(db: Session, user: User, factor_id: str, code: str, *, request_id: str | None) -> None:
  roles = {role.role for role in user.roles}
  if settings.admin_mfa_required and "ADMIN" in roles:
    raise AppError(409, "ADMIN_MFA_REQUIRED", "Admin authenticator MFA cannot be removed while the policy is enabled.")
  factor = active_factor(db, user.id)
  if not factor or factor.id != factor_id:
    raise AppError(404, "MFA_FACTOR_NOT_FOUND", "Authenticator factor was not found.")
  if not _verify_totp(factor, code):
    raise AppError(422, "MFA_CODE_INVALID", "A current authenticator code is required.")
  factor.disabled_at = utc_now()
  db.execute(delete(MfaRecoveryCode).where(MfaRecoveryCode.factor_id == factor.id))
  write_audit_log(db, event_type="MFA_FACTOR_DISABLED", actor_user_id=user.id, target_user_id=user.id, request_id=request_id)
