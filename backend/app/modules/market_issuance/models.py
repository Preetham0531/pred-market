from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DataSource(UUIDPrimaryKeyMixin, TimestampMixin, Base):
  __tablename__ = "data_sources"
  __table_args__ = (UniqueConstraint("name", "provider", name="uq_data_sources_name_provider"),)

  name: Mapped[str] = mapped_column(String(180), nullable=False)
  provider: Mapped[str] = mapped_column(String(120), nullable=False)
  source_type: Mapped[str] = mapped_column(String(60), nullable=False)
  category_slug: Mapped[str] = mapped_column(String(80), ForeignKey("categories.slug"), nullable=False, index=True)
  base_url: Mapped[str] = mapped_column(Text, nullable=False)
  license_status: Mapped[str] = mapped_column(String(80), nullable=False, default="REVIEW_REQUIRED")
  automation_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
  refresh_schedule: Mapped[str] = mapped_column(String(120), nullable=False, default="MANUAL")
  settlement_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
  discovery_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
  status: Mapped[str] = mapped_column(String(60), nullable=False, default="ACTIVE")
  health_status: Mapped[str] = mapped_column(String(60), nullable=False, default="UNKNOWN")
  last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
  config_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
  notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class SourceEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
  __tablename__ = "source_events"
  __table_args__ = (UniqueConstraint("data_source_id", "dedupe_key", name="uq_source_events_source_dedupe"),)

  data_source_id: Mapped[str] = mapped_column(String(36), ForeignKey("data_sources.id"), nullable=False, index=True)
  category_slug: Mapped[str] = mapped_column(String(80), ForeignKey("categories.slug"), nullable=False, index=True)
  external_id: Mapped[str | None] = mapped_column(String(240), nullable=True)
  title: Mapped[str] = mapped_column(Text, nullable=False)
  url: Mapped[str | None] = mapped_column(Text, nullable=True)
  published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
  source_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
  raw_payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
  content_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
  dedupe_key: Mapped[str] = mapped_column(String(260), nullable=False)
  credibility_score: Mapped[int] = mapped_column(Integer, nullable=False, default=70)
  ingestion_status: Mapped[str] = mapped_column(String(60), nullable=False, default="INGESTED")
  ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

  data_source: Mapped[DataSource] = relationship("DataSource")


class MarketDraft(UUIDPrimaryKeyMixin, TimestampMixin, Base):
  __tablename__ = "market_drafts"

  origin: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
  created_by_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
  suggestion_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("market_suggestions.id"), nullable=True)
  listed_market_id: Mapped[str | None] = mapped_column(String(120), ForeignKey("markets.id"), nullable=True)
  category_slug: Mapped[str] = mapped_column(String(80), ForeignKey("categories.slug"), nullable=False, index=True)
  subcategory: Mapped[str] = mapped_column(String(120), nullable=False, default="General")
  market_type: Mapped[str] = mapped_column(String(60), nullable=False)
  question: Mapped[str] = mapped_column(Text, nullable=False)
  outcomes_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
  close_time: Mapped[str] = mapped_column(String(120), nullable=False, default="Admin must set close time")
  source: Mapped[str] = mapped_column(Text, nullable=False)
  resolution_rule: Mapped[str] = mapped_column(Text, nullable=False)
  void_policy: Mapped[str] = mapped_column(Text, nullable=False)
  settlement_source_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("data_sources.id"), nullable=True)
  discovery_source_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("data_sources.id"), nullable=True)
  status: Mapped[str] = mapped_column(String(60), nullable=False, default="DRAFT", index=True)
  checks_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
  risk_flags_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
  ai_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
  confidence_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
  admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

  evidence: Mapped[list["MarketDraftEvidence"]] = relationship("MarketDraftEvidence", back_populates="draft", cascade="all, delete-orphan")


class MarketDraftEvidence(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "market_draft_evidence"

  draft_id: Mapped[str] = mapped_column(String(36), ForeignKey("market_drafts.id"), nullable=False, index=True)
  source_event_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("source_events.id"), nullable=True)
  data_source_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("data_sources.id"), nullable=True)
  title: Mapped[str] = mapped_column(Text, nullable=False)
  url: Mapped[str | None] = mapped_column(Text, nullable=True)
  evidence_type: Mapped[str] = mapped_column(String(60), nullable=False, default="SOURCE_EVENT")
  snapshot_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

  draft: Mapped[MarketDraft] = relationship("MarketDraft", back_populates="evidence")
