from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.db.base import Base
from app.modules.admin.models import AdminReview
from app.modules.analytics.models import CategoryAnalytics, MarketAnalytics, UserAnalytics
from app.modules.audit.models import AuditLog
from app.modules.auth.models import AdminImpersonationSession, AuthSession, EmailVerificationToken, PasswordResetToken
from app.modules.market_suggestions.models import MarketSuggestion
from app.modules.markets.models import Category, Market, MarketRule, OracleEvidence, Outcome
from app.modules.market_issuance.models import DataSource, MarketDraft, MarketDraftEvidence, SourceEvent
from app.modules.orders.models import Order
from app.modules.positions.models import Position
from app.modules.realtime.models import RealtimeEvent
from app.modules.settlement.models import ResolutionProposal, Settlement, SettlementItem
from app.modules.trades.models import Trade
from app.modules.users.models import User, UserRole
from app.modules.wallets.models import LedgerAccount, LedgerEntry, LedgerTransaction, Wallet
from app.modules.watchlist.models import WatchlistItem

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
  fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
  context.configure(
    url=settings.database_url,
    target_metadata=target_metadata,
    literal_binds=True,
    dialect_opts={"paramstyle": "named"},
  )

  with context.begin_transaction():
    context.run_migrations()


def run_migrations_online() -> None:
  connectable = engine_from_config(
    config.get_section(config.config_ini_section, {}),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
  )

  with connectable.connect() as connection:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
      context.run_migrations()


if context.is_offline_mode():
  run_migrations_offline()
else:
  run_migrations_online()
