from fastapi import APIRouter, Depends, Header, Query, Request
from sqlalchemy.orm import Session

from app.core.rate_limit import check_rate_limit
from app.core.public_ids import public_id
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user, get_current_user_for_write
from app.modules.realtime.service import publish_pending_events
from app.modules.users.models import User
from app.modules.wallets.schemas import LedgerPage, TestDepositRequest, WalletResponse
from app.modules.wallets.service import get_or_create_wallet, list_ledger_entries, test_deposit, wallet_to_response

router = APIRouter()


@router.get("", response_model=WalletResponse)
def wallet_endpoint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
  return wallet_to_response(get_or_create_wallet(db, user.id))


@router.get("/ledger", response_model=LedgerPage)
def wallet_ledger_endpoint(
  limit: int = Query(default=50, ge=1, le=100),
  user: User = Depends(get_current_user),
  db: Session = Depends(get_db),
):
  entries = list_ledger_entries(db, user_id=user.id, limit=limit)
  return {
    "items": [
      {
        "id": public_id("LED", entry.id),
        "transaction_id": public_id("TXN", entry.transaction_id),
        "account_type": entry.account.account_type,
        "side": entry.side,
        "amount_minor": entry.amount_minor,
        "currency": entry.currency,
        "created_at": entry.created_at,
      }
      for entry in entries
    ],
    "next_cursor": None,
  }


@router.post("/test-deposit", response_model=WalletResponse)
async def wallet_test_deposit_endpoint(
  payload: TestDepositRequest,
  request: Request,
  idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
  user: User = Depends(get_current_user_for_write),
  db: Session = Depends(get_db),
):
  check_rate_limit(key=f"wallet:test-deposit:user:{user.id}", limit=20, window_seconds=60)
  wallet = test_deposit(
    db,
    user=user,
    amount_minor=payload.amount_minor,
    currency=payload.currency.upper(),
    idempotency_key=idempotency_key,
    request_id=getattr(request.state, "request_id", None),
  )
  db.commit()
  await publish_pending_events(db)
  db.commit()
  return wallet_to_response(wallet)
