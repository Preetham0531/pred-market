from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MarketSuggestionCreate(BaseModel):
  category_slug: str
  market_type: str
  question: str = Field(min_length=8)
  outcomes: list[str] = Field(default_factory=lambda: ["YES", "NO"])
  source: str = Field(min_length=3)
  resolution_rule: str = Field(min_length=8)


class MarketSuggestionResponse(BaseModel):
  id: str
  draft_id: str | None = None
  submitted_by_user_id: str
  category_slug: str
  market_type: str
  question: str
  outcomes: list[str]
  source: str
  resolution_rule: str
  status: str
  checks: dict[str, Any]
  created_at: datetime
  updated_at: datetime
