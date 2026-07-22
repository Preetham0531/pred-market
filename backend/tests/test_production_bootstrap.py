from sqlalchemy import func, select

from app.core.security import verify_password
from app.modules.audit.models import AuditLog
from app.modules.market_issuance.models import DataSource
from app.modules.markets.models import Category, Market
from app.modules.users.models import User
from app.modules.wallets.models import Wallet
from app.seed.create_admin import bootstrap_admin_in_session
from app.seed.staging import seed_staging_database


def test_staging_seed_is_curated_labeled_and_idempotent(db_session):
  first = seed_staging_database(db_session)
  db_session.commit()
  second = seed_staging_database(db_session)
  db_session.commit()

  assert first == second
  assert second["categories"] == 10
  assert second["markets"] == 6
  assert db_session.scalar(select(func.count()).select_from(Category)) == 10
  assert db_session.scalar(select(func.count()).select_from(Market)) == 6
  assert db_session.scalar(select(func.count()).select_from(DataSource)) == second["sources"]
  assert all(market.title.startswith("Simulation:") for market in db_session.scalars(select(Market)).all())


def test_admin_bootstrap_creates_verified_admin_wallet_without_overwriting_password(db_session):
  email = "bootstrap-owner@predmarket.dev"
  first_password = "FirstStrongPass123"
  result = bootstrap_admin_in_session(db_session, email=email, password=first_password)
  db_session.commit()

  user = db_session.scalar(select(User).where(User.email == email))
  assert result == "created"
  assert user is not None
  assert user.email_verified_at is not None
  assert {role.role for role in user.roles} == {"USER", "ADMIN"}
  assert verify_password(first_password, user.password_hash)
  assert db_session.scalar(select(Wallet).where(Wallet.user_id == user.id)) is not None

  repeated = bootstrap_admin_in_session(db_session, email=email, password="DifferentStrongPass123")
  db_session.commit()
  db_session.refresh(user)
  assert repeated == "already-present"
  assert verify_password(first_password, user.password_hash)
  assert not verify_password("DifferentStrongPass123", user.password_hash)
  assert db_session.scalar(select(AuditLog).where(AuditLog.event_type == "ADMIN_BOOTSTRAPPED")) is not None
