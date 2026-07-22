import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings
from app.core.errors import AppError

_password_hasher = PasswordHasher()


def utc_now() -> datetime:
  return datetime.now(UTC)


def as_utc(value: datetime) -> datetime:
  if value.tzinfo is None:
    return value.replace(tzinfo=UTC)
  return value.astimezone(UTC)


def expires_in(seconds: int) -> datetime:
  return utc_now() + timedelta(seconds=seconds)


def hash_password(password: str) -> str:
  return _password_hasher.hash(password)


def validate_password_strength(password: str) -> None:
  if len(password) < 12 or not any(char.islower() for char in password) or not any(char.isupper() for char in password) or not any(char.isdigit() for char in password):
    raise AppError(422, "WEAK_PASSWORD", "Password must be at least 12 characters and include uppercase, lowercase, and a number.")


def verify_password(password: str, password_hash: str) -> bool:
  try:
    return _password_hasher.verify(password_hash, password)
  except VerifyMismatchError:
    return False


def new_token(byte_length: int = 32) -> str:
  return secrets.token_urlsafe(byte_length)


def hash_token(token: str) -> str:
  return hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_optional(value: str | None) -> str | None:
  if not value:
    return None
  return hash_token(value)


def create_jwt(payload: dict[str, Any], *, ttl_seconds: int) -> str:
  now = utc_now()
  claims = {**payload, "iat": int(now.timestamp()), "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp())}
  return jwt.encode(claims, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_jwt(token: str) -> dict[str, Any]:
  try:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
  except jwt.ExpiredSignatureError as exc:
    raise AppError(401, "TOKEN_EXPIRED", "Session access token has expired.") from exc
  except jwt.InvalidTokenError as exc:
    raise AppError(401, "UNAUTHENTICATED", "Session access token is invalid.") from exc
