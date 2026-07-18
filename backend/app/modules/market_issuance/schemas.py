from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class DataSourceCreate(BaseModel):
  name: str = Field(min_length=3)
  provider: str = Field(min_length=2)
  source_type: str
  category_slug: str
  base_url: str = Field(min_length=5)
  license_status: str = "REVIEW_REQUIRED"
  automation_level: int = Field(default=1, ge=0, le=3)
  refresh_schedule: str = "MANUAL"
  settlement_eligible: bool = False
  discovery_eligible: bool = True
  status: str = "ACTIVE"
  config: dict[str, Any] = Field(default_factory=dict)
  notes: str | None = None


class DataSourceResponse(BaseModel):
  id: str
  name: str
  provider: str
  source_type: str
  category_slug: str
  base_url: str
  license_status: str
  automation_level: int
  refresh_schedule: str
  settlement_eligible: bool
  discovery_eligible: bool
  status: str
  health_status: str
  last_checked_at: datetime | None
  config: dict[str, Any]
  notes: str | None
  created_at: datetime
  updated_at: datetime


class DataSourceList(BaseModel):
  items: list[DataSourceResponse]
  next_cursor: str | None = None


class DataSourceTestResponse(BaseModel):
  source_id: str
  status: str
  health_status: str
  checked_at: datetime
  message: str


class SourceEventResponse(BaseModel):
  id: str
  data_source_id: str
  category_slug: str
  title: str
  url: str | None
  published_at: datetime | None
  source_timestamp: datetime | None
  content_hash: str
  dedupe_key: str
  credibility_score: int
  ingestion_status: str
  ingested_at: datetime
  created_at: datetime


class SourceEventList(BaseModel):
  items: list[SourceEventResponse]
  next_cursor: str | None = None


class IngestionRunCreate(BaseModel):
  source_id: str | None = None
  category_slug: str | None = None
  query: str | None = None
  limit: int = Field(default=5, ge=1, le=25)


class IngestionRunResponse(BaseModel):
  status: str
  created_events: int
  skipped_duplicates: int
  items: list[SourceEventResponse]


class DraftEvidenceResponse(BaseModel):
  id: str
  source_event_id: str | None
  data_source_id: str | None
  title: str
  url: str | None
  evidence_type: str
  snapshot: dict[str, Any]
  created_at: datetime


class MarketDraftCreate(BaseModel):
  origin: Literal["AI", "ADMIN", "TRADER"] = "ADMIN"
  category_slug: str
  subcategory: str = "General"
  market_type: str = "Binary"
  question: str = Field(min_length=8)
  outcomes: list[str] = Field(default_factory=lambda: ["YES", "NO"])
  close_time: str = Field(min_length=3)
  source: str = Field(min_length=3)
  resolution_rule: str = Field(min_length=8)
  void_policy: str = "Void only if the approved source is unavailable or the market rule explicitly requires voiding."
  settlement_source_id: str | None = None
  discovery_source_id: str | None = None
  ai_rationale: str | None = None
  confidence_score: int | None = Field(default=None, ge=0, le=100)
  admin_notes: str | None = None
  list_immediately: bool = False


class MarketDraftPatch(BaseModel):
  category_slug: str | None = None
  subcategory: str | None = None
  market_type: str | None = None
  question: str | None = None
  outcomes: list[str] | None = None
  close_time: str | None = None
  source: str | None = None
  resolution_rule: str | None = None
  void_policy: str | None = None
  settlement_source_id: str | None = None
  discovery_source_id: str | None = None
  ai_rationale: str | None = None
  confidence_score: int | None = Field(default=None, ge=0, le=100)
  admin_notes: str | None = None


class MarketDraftResponse(BaseModel):
  id: str
  origin: str
  created_by_user_id: str | None
  suggestion_id: str | None
  listed_market_id: str | None
  category_slug: str
  subcategory: str
  market_type: str
  question: str
  outcomes: list[str]
  close_time: str
  source: str
  resolution_rule: str
  void_policy: str
  settlement_source_id: str | None
  discovery_source_id: str | None
  status: str
  checks: dict[str, Any]
  risk_flags: list[str]
  ai_rationale: str | None
  confidence_score: int | None
  admin_notes: str | None
  evidence: list[DraftEvidenceResponse]
  created_at: datetime
  updated_at: datetime


class MarketDraftList(BaseModel):
  items: list[MarketDraftResponse]
  next_cursor: str | None = None


class MarketDraftActionResponse(BaseModel):
  status: str
  draft_id: str
  market_id: str | None = None


class AIMarketGenerationRunRequest(BaseModel):
  source_event_id: str | None = None
  category_slug: str | None = None
  limit: int = Field(default=3, ge=1, le=10)


class AIMarketGenerationRunResponse(BaseModel):
  status: str
  created_drafts: int
  items: list[MarketDraftResponse]
