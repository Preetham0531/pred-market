from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

  app_name: str = "Pred-Market Backend"
  environment: str = "development"
  api_v1_prefix: str = "/api/v1"
  version: str = "0.1.0"
  database_url: str = "postgresql+psycopg://pred_market:pred_market@localhost:5433/pred_market"
  redis_url: str = "redis://localhost:6379/0"
  cors_origins: str = "http://localhost:3000"
  cookie_secure: bool = False
  access_cookie_name: str = "pred_market_v1_access_token"
  refresh_cookie_name: str = "pred_market_v1_refresh_token"
  csrf_cookie_name: str = "pred_market_v1_csrf_token"
  mfa_challenge_cookie_name: str = "pred_market_v1_mfa_challenge"
  session_ttl_seconds: int = 7 * 24 * 60 * 60
  access_token_ttl_seconds: int = 10 * 60
  jwt_secret_key: str = "dev-change-me-pred-market-jwt-secret"
  jwt_algorithm: str = "HS256"
  account_lock_threshold: int = 5
  account_lock_minutes: int = 15
  demo_seed_enabled: bool = True
  public_signup_enabled: bool = True
  email_verification_required: bool = False
  admin_mfa_required: bool = False
  mfa_challenge_ttl_seconds: int = 5 * 60
  mfa_encryption_key: str = ""
  frontend_base_url: str = "http://localhost:3000"
  email_delivery_enabled: bool = False
  resend_api_key: str = ""
  resend_from: str = "Pred-Market <onboarding@resend.dev>"
  admin_bootstrap_email: str = ""
  admin_bootstrap_password: str = ""

  @field_validator("database_url", mode="before")
  @classmethod
  def use_psycopg_driver(cls, value: str) -> str:
    if value.startswith("postgres://"):
      return value.replace("postgres://", "postgresql+psycopg://", 1)
    if value.startswith("postgresql://"):
      return value.replace("postgresql://", "postgresql+psycopg://", 1)
    return value

  @property
  def cors_origin_list(self) -> list[str]:
    return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
  return Settings()


settings = get_settings()
