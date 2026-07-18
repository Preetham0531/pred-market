from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EvidenceCreate(BaseModel):
  source_name: str = Field(min_length=2, max_length=160)
  source_url: str | None = None
  captured_payload: dict[str, Any] = Field(default_factory=dict)


class ResolutionProposalCreate(BaseModel):
  result: str = Field(pattern="^(RESOLVE|VOID)$")
  winning_outcome_id: str | None = None
  reason: str = Field(min_length=10, max_length=3000)


class ResolutionProposalResponse(BaseModel):
  id: str
  market_id: str
  winning_outcome_id: str | None
  result: str
  reason: str
  maker_user_id: str
  checker_user_id: str | None
  status: str
  created_at: datetime
  approved_at: datetime | None


class EvidenceResponse(BaseModel):
  id: str
  market_id: str
  source_name: str
  source_url: str | None
  captured_payload: dict[str, Any]
  captured_at: datetime


class SettlementItemResponse(BaseModel):
  id: str
  user_id: str
  position_id: str
  payout_minor: int
  created_at: datetime


class SettlementResponse(BaseModel):
  id: str
  market_id: str
  resolution_proposal_id: str
  status: str
  completed_at: datetime | None
  items: list[SettlementItemResponse]
