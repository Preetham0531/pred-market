from app.core.config import Settings


def test_railway_postgres_url_uses_psycopg_driver() -> None:
  settings = Settings(
    _env_file=None,
    database_url="postgresql://user:password@postgres.railway.internal:5432/railway",
  )

  assert settings.database_url == (
    "postgresql+psycopg://user:password@postgres.railway.internal:5432/railway"
  )


def test_legacy_postgres_url_uses_psycopg_driver() -> None:
  settings = Settings(
    _env_file=None,
    database_url="postgres://user:password@postgres.railway.internal:5432/railway",
  )

  assert settings.database_url == (
    "postgresql+psycopg://user:password@postgres.railway.internal:5432/railway"
  )


def test_sqlite_url_is_unchanged() -> None:
  settings = Settings(_env_file=None, database_url="sqlite://")

  assert settings.database_url == "sqlite://"
