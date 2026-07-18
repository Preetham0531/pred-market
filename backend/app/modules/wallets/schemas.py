from datetime import datetime

from pydantic import BaseModel, Field


class MoneyResponse(BaseModel):
  amount_minor: int
  currency: str = "INR"


class WalletResponse(BaseModel):
  available: MoneyResponse
  locked: MoneyResponse
  total: MoneyResponse


class TestDepositRequest(BaseModel):
  amount_minor: int = Field(gt=0, le=50_000_000)
  currency: str = Field(default="INR", min_length=3, max_length=3)


class LedgerEntryResponse(BaseModel):
  id: str
  transaction_id: str
  account_type: str
  side: str
  amount_minor: int
  currency: str
  created_at: datetime


class LedgerPage(BaseModel):
  items: list[LedgerEntryResponse]
  next_cursor: str | None = None
