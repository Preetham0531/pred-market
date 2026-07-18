import json
from hashlib import sha256
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import AppError
from app.modules.realtime.service import write_user_event
from app.modules.audit.service import write_audit_log
from app.modules.users.models import User
from app.modules.wallets.models import LedgerAccount, LedgerEntry, LedgerTransaction, Wallet

DEFAULT_CURRENCY = "INR"


def request_hash(payload: dict[str, Any]) -> str:
  return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def get_or_create_wallet(db: Session, user_id: str, currency: str = DEFAULT_CURRENCY) -> Wallet:
  wallet = db.scalar(select(Wallet).where(Wallet.user_id == user_id, Wallet.currency == currency))
  if wallet:
    return wallet
  wallet = Wallet(user_id=user_id, currency=currency, available_balance_minor=0, locked_balance_minor=0)
  db.add(wallet)
  db.flush()
  get_or_create_account(db, owner_type="USER", owner_id=user_id, account_type="USER_AVAILABLE_CASH", currency=currency)
  get_or_create_account(db, owner_type="USER", owner_id=user_id, account_type="USER_LOCKED_CASH", currency=currency)
  return wallet


def get_or_create_account(db: Session, *, owner_type: str, owner_id: str | None, account_type: str, currency: str) -> LedgerAccount:
  account = db.scalar(
    select(LedgerAccount).where(
      LedgerAccount.owner_type == owner_type,
      LedgerAccount.owner_id == owner_id,
      LedgerAccount.account_type == account_type,
      LedgerAccount.currency == currency,
    )
  )
  if account:
    return account
  account = LedgerAccount(
    owner_type=owner_type,
    owner_id=owner_id,
    account_type=account_type,
    currency=currency,
    name=f"{owner_type}:{owner_id or 'platform'}:{account_type}:{currency}",
  )
  db.add(account)
  db.flush()
  return account


def create_balanced_transaction(
  db: Session,
  *,
  transaction_type: str,
  idempotency_key: str | None,
  request_hash_value: str | None,
  reference_type: str | None,
  reference_id: str | None,
  metadata: dict[str, Any] | None,
  entries: list[tuple[LedgerAccount, str, int]],
) -> LedgerTransaction:
  if idempotency_key:
    existing = db.scalar(
      select(LedgerTransaction)
      .where(LedgerTransaction.idempotency_key == idempotency_key)
      .options(selectinload(LedgerTransaction.entries))
    )
    if existing:
      if existing.request_hash != request_hash_value:
        raise AppError(409, "IDEMPOTENCY_CONFLICT", "Idempotency key was reused with different request data.")
      return existing

  debit_total = sum(amount for _, side, amount in entries if side == "DEBIT")
  credit_total = sum(amount for _, side, amount in entries if side == "CREDIT")
  if debit_total <= 0 or debit_total != credit_total:
    raise AppError(500, "UNBALANCED_LEDGER_TRANSACTION", "Ledger transaction is not balanced.")

  tx = LedgerTransaction(
    transaction_type=transaction_type,
    idempotency_key=idempotency_key,
    request_hash=request_hash_value,
    reference_type=reference_type,
    reference_id=reference_id,
    metadata_json=metadata or {},
  )
  db.add(tx)
  db.flush()
  for account, side, amount in entries:
    db.add(LedgerEntry(transaction_id=tx.id, account_id=account.id, side=side, amount_minor=amount, currency=account.currency))
  return tx


def wallet_to_response(wallet: Wallet) -> dict:
  total = wallet.available_balance_minor + wallet.locked_balance_minor
  return {
    "available": {"amount_minor": wallet.available_balance_minor, "currency": wallet.currency},
    "locked": {"amount_minor": wallet.locked_balance_minor, "currency": wallet.currency},
    "total": {"amount_minor": total, "currency": wallet.currency},
  }


def test_deposit(
  db: Session,
  *,
  user: User,
  amount_minor: int,
  currency: str,
  idempotency_key: str | None,
  request_id: str | None,
) -> Wallet:
  wallet = get_or_create_wallet(db, user.id, currency)
  req_hash = request_hash({"user_id": user.id, "amount_minor": amount_minor, "currency": currency})
  existing = None
  if idempotency_key:
    existing = db.scalar(select(LedgerTransaction).where(LedgerTransaction.idempotency_key == idempotency_key))
  if existing:
    if existing.request_hash != req_hash:
      raise AppError(409, "IDEMPOTENCY_CONFLICT", "Idempotency key was reused with different request data.")
    return wallet

  wallet.available_balance_minor += amount_minor
  external = get_or_create_account(db, owner_type="PLATFORM", owner_id=None, account_type="EXTERNAL_DEPOSIT_CLEARING", currency=currency)
  available = get_or_create_account(db, owner_type="USER", owner_id=user.id, account_type="USER_AVAILABLE_CASH", currency=currency)
  create_balanced_transaction(
    db,
    transaction_type="DEPOSIT",
    idempotency_key=idempotency_key,
    request_hash_value=req_hash,
    reference_type="USER",
    reference_id=user.id,
    metadata={"simulated": True},
    entries=[(external, "DEBIT", amount_minor), (available, "CREDIT", amount_minor)],
  )
  write_audit_log(db, event_type="TEST_DEPOSIT_CREATED", actor_user_id=user.id, target_user_id=user.id, request_id=request_id, metadata={"amount_minor": amount_minor})
  write_user_event(
    db,
    event_type="wallet.updated",
    user_id=user.id,
    suffix="wallet",
    payload={"available": wallet.available_balance_minor, "locked": wallet.locked_balance_minor, "reason": "TEST_DEPOSIT"},
  )
  return wallet


def lock_cash_for_order(db: Session, *, user_id: str, amount_minor: int, order_id: str, idempotency_key: str | None) -> Wallet:
  wallet = get_or_create_wallet(db, user_id)
  if wallet.available_balance_minor < amount_minor:
    raise AppError(402, "INSUFFICIENT_FUNDS", "Available balance is not sufficient for this order.")
  wallet.available_balance_minor -= amount_minor
  wallet.locked_balance_minor += amount_minor
  available = get_or_create_account(db, owner_type="USER", owner_id=user_id, account_type="USER_AVAILABLE_CASH", currency=wallet.currency)
  locked = get_or_create_account(db, owner_type="USER", owner_id=user_id, account_type="USER_LOCKED_CASH", currency=wallet.currency)
  create_balanced_transaction(
    db,
    transaction_type="ORDER_LOCK",
    idempotency_key=idempotency_key,
    request_hash_value=request_hash({"order_id": order_id, "amount_minor": amount_minor}),
    reference_type="ORDER",
    reference_id=order_id,
    metadata={},
    entries=[(available, "DEBIT", amount_minor), (locked, "CREDIT", amount_minor)],
  )
  write_user_event(
    db,
    event_type="wallet.updated",
    user_id=user_id,
    suffix="wallet",
    payload={"available": wallet.available_balance_minor, "locked": wallet.locked_balance_minor, "reason": "ORDER_LOCK", "order_id": order_id},
  )
  return wallet


def release_locked_cash(db: Session, *, user_id: str, amount_minor: int, reference_id: str, transaction_type: str = "ORDER_RELEASE") -> None:
  if amount_minor <= 0:
    return
  wallet = get_or_create_wallet(db, user_id)
  if wallet.locked_balance_minor < amount_minor:
    raise AppError(500, "LOCKED_BALANCE_UNDERFLOW", "Locked balance would become negative.")
  wallet.locked_balance_minor -= amount_minor
  wallet.available_balance_minor += amount_minor
  locked = get_or_create_account(db, owner_type="USER", owner_id=user_id, account_type="USER_LOCKED_CASH", currency=wallet.currency)
  available = get_or_create_account(db, owner_type="USER", owner_id=user_id, account_type="USER_AVAILABLE_CASH", currency=wallet.currency)
  create_balanced_transaction(
    db,
    transaction_type=transaction_type,
    idempotency_key=f"{transaction_type}:{reference_id}:{user_id}:{amount_minor}",
    request_hash_value=request_hash({"reference_id": reference_id, "user_id": user_id, "amount_minor": amount_minor}),
    reference_type="ORDER",
    reference_id=reference_id,
    metadata={},
    entries=[(locked, "DEBIT", amount_minor), (available, "CREDIT", amount_minor)],
  )
  write_user_event(
    db,
    event_type="wallet.updated",
    user_id=user_id,
    suffix="wallet",
    payload={"available": wallet.available_balance_minor, "locked": wallet.locked_balance_minor, "reason": transaction_type, "reference_id": reference_id},
  )


def move_locked_cash_to_market_collateral(db: Session, *, user_id: str, market_id: str, amount_minor: int, reference_id: str) -> None:
  if amount_minor <= 0:
    return
  wallet = get_or_create_wallet(db, user_id)
  if wallet.locked_balance_minor < amount_minor:
    raise AppError(500, "LOCKED_BALANCE_UNDERFLOW", "Locked balance would become negative.")
  wallet.locked_balance_minor -= amount_minor
  locked = get_or_create_account(db, owner_type="USER", owner_id=user_id, account_type="USER_LOCKED_CASH", currency=wallet.currency)
  collateral = get_or_create_account(db, owner_type="MARKET", owner_id=market_id, account_type="MARKET_COLLATERAL", currency=wallet.currency)
  create_balanced_transaction(
    db,
    transaction_type="TRADE_COLLATERAL",
    idempotency_key=f"TRADE_COLLATERAL:{reference_id}:{user_id}:{amount_minor}",
    request_hash_value=request_hash({"reference_id": reference_id, "user_id": user_id, "amount_minor": amount_minor}),
    reference_type="TRADE",
    reference_id=reference_id,
    metadata={},
    entries=[(locked, "DEBIT", amount_minor), (collateral, "CREDIT", amount_minor)],
  )
  write_user_event(
    db,
    event_type="wallet.updated",
    user_id=user_id,
    suffix="wallet",
    market_id=market_id,
    payload={"available": wallet.available_balance_minor, "locked": wallet.locked_balance_minor, "reason": "TRADE_COLLATERAL", "reference_id": reference_id},
  )


def credit_available_cash(db: Session, *, user_id: str, market_id: str, amount_minor: int, reference_id: str, transaction_type: str) -> None:
  if amount_minor <= 0:
    return
  wallet = get_or_create_wallet(db, user_id)
  wallet.available_balance_minor += amount_minor
  collateral = get_or_create_account(db, owner_type="MARKET", owner_id=market_id, account_type="MARKET_COLLATERAL", currency=wallet.currency)
  available = get_or_create_account(db, owner_type="USER", owner_id=user_id, account_type="USER_AVAILABLE_CASH", currency=wallet.currency)
  create_balanced_transaction(
    db,
    transaction_type=transaction_type,
    idempotency_key=f"{transaction_type}:{reference_id}:{user_id}:{amount_minor}",
    request_hash_value=request_hash({"market_id": market_id, "reference_id": reference_id, "user_id": user_id, "amount_minor": amount_minor}),
    reference_type="SETTLEMENT",
    reference_id=reference_id,
    metadata={},
    entries=[(collateral, "DEBIT", amount_minor), (available, "CREDIT", amount_minor)],
  )
  write_user_event(
    db,
    event_type="wallet.updated",
    user_id=user_id,
    suffix="wallet",
    market_id=market_id,
    payload={"available": wallet.available_balance_minor, "locked": wallet.locked_balance_minor, "reason": transaction_type, "reference_id": reference_id},
  )


def transfer_locked_cash_to_user_available(
  db: Session,
  *,
  from_user_id: str,
  to_user_id: str,
  amount_minor: int,
  reference_id: str,
) -> None:
  if amount_minor <= 0:
    return
  from_wallet = get_or_create_wallet(db, from_user_id)
  to_wallet = get_or_create_wallet(db, to_user_id, from_wallet.currency)
  if from_wallet.locked_balance_minor < amount_minor:
    raise AppError(500, "LOCKED_BALANCE_UNDERFLOW", "Locked balance would become negative.")
  from_wallet.locked_balance_minor -= amount_minor
  to_wallet.available_balance_minor += amount_minor
  locked = get_or_create_account(db, owner_type="USER", owner_id=from_user_id, account_type="USER_LOCKED_CASH", currency=from_wallet.currency)
  available = get_or_create_account(db, owner_type="USER", owner_id=to_user_id, account_type="USER_AVAILABLE_CASH", currency=from_wallet.currency)
  create_balanced_transaction(
    db,
    transaction_type="POSITION_TRANSFER",
    idempotency_key=f"POSITION_TRANSFER:{reference_id}:{from_user_id}:{to_user_id}:{amount_minor}",
    request_hash_value=request_hash({"reference_id": reference_id, "from_user_id": from_user_id, "to_user_id": to_user_id, "amount_minor": amount_minor}),
    reference_type="TRADE",
    reference_id=reference_id,
    metadata={},
    entries=[(locked, "DEBIT", amount_minor), (available, "CREDIT", amount_minor)],
  )
  write_user_event(
    db,
    event_type="wallet.updated",
    user_id=from_user_id,
    suffix="wallet",
    payload={"available": from_wallet.available_balance_minor, "locked": from_wallet.locked_balance_minor, "reason": "POSITION_TRANSFER", "reference_id": reference_id},
  )
  write_user_event(
    db,
    event_type="wallet.updated",
    user_id=to_user_id,
    suffix="wallet",
    payload={"available": to_wallet.available_balance_minor, "locked": to_wallet.locked_balance_minor, "reason": "POSITION_TRANSFER", "reference_id": reference_id},
  )


def list_ledger_entries(db: Session, *, user_id: str, limit: int) -> list[LedgerEntry]:
  account_ids = [
    account.id
    for account in db.scalars(
      select(LedgerAccount).where(LedgerAccount.owner_type == "USER", LedgerAccount.owner_id == user_id)
    ).all()
  ]
  if not account_ids:
    return []
  return list(
    db.scalars(
      select(LedgerEntry)
      .where(LedgerEntry.account_id.in_(account_ids))
      .options(selectinload(LedgerEntry.account))
      .order_by(LedgerEntry.created_at.desc())
      .limit(limit)
    ).all()
  )
