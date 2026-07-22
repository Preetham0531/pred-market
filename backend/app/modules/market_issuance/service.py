from __future__ import annotations

import hashlib
import re
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.errors import AppError
from app.core.public_ids import matches_public_id, public_id
from app.core.security import utc_now
from app.modules.admin.models import AdminReview
from app.modules.audit.service import write_audit_log
from app.modules.markets.models import Category, Market, MarketRule, OracleEvidence, Outcome
from app.modules.market_issuance.models import DataSource, MarketDraft, MarketDraftEvidence, SourceEvent
from app.modules.realtime.service import write_admin_event, write_market_event
from app.modules.users.models import User

ALLOWED_MARKET_TYPES = {"Binary", "Multiple-choice", "Range", "Threshold", "Conditional", "Combo"}
PROHIBITED_TERMS = {"death", "assassination", "terror", "violence", "personal health"}
RESTRICTED_CATEGORIES = {"politics", "stocks-mutual-funds", "financials", "commodities", "mentions"}
TERMINAL_DRAFT_STATUSES = {"REJECTED", "ARCHIVED", "LISTED"}


def source_to_response(source: DataSource) -> dict:
  return {
    "id": public_id("SRC", source.id),
    "name": source.name,
    "provider": source.provider,
    "source_type": source.source_type,
    "category_slug": source.category_slug,
    "base_url": source.base_url,
    "license_status": source.license_status,
    "automation_level": source.automation_level,
    "refresh_schedule": source.refresh_schedule,
    "settlement_eligible": source.settlement_eligible,
    "discovery_eligible": source.discovery_eligible,
    "status": source.status,
    "health_status": source.health_status,
    "last_checked_at": source.last_checked_at,
    "config": source.config_json,
    "notes": source.notes,
    "created_at": source.created_at,
    "updated_at": source.updated_at,
  }


def event_to_response(event: SourceEvent) -> dict:
  return {
    "id": public_id("EVS", event.id),
    "data_source_id": public_id("SRC", event.data_source_id),
    "category_slug": event.category_slug,
    "title": event.title,
    "url": event.url,
    "published_at": event.published_at,
    "source_timestamp": event.source_timestamp,
    "content_hash": event.content_hash,
    "dedupe_key": event.dedupe_key,
    "credibility_score": event.credibility_score,
    "ingestion_status": event.ingestion_status,
    "ingested_at": event.ingested_at,
    "created_at": event.created_at,
  }


def evidence_to_response(evidence: MarketDraftEvidence) -> dict:
  return {
    "id": public_id("DVE", evidence.id),
    "source_event_id": public_id("EVS", evidence.source_event_id),
    "data_source_id": public_id("SRC", evidence.data_source_id),
    "title": evidence.title,
    "url": evidence.url,
    "evidence_type": evidence.evidence_type,
    "snapshot": evidence.snapshot_json,
    "created_at": evidence.created_at,
  }


def draft_to_response(draft: MarketDraft) -> dict:
  return {
    "id": public_id("DRF", draft.id),
    "origin": draft.origin,
    "created_by_user_id": public_id("USR", draft.created_by_user_id),
    "suggestion_id": public_id("SUG", draft.suggestion_id),
    "listed_market_id": draft.listed_market_id,
    "category_slug": draft.category_slug,
    "subcategory": draft.subcategory,
    "market_type": draft.market_type,
    "question": draft.question,
    "outcomes": draft.outcomes_json,
    "close_time": draft.close_time,
    "source": draft.source,
    "resolution_rule": draft.resolution_rule,
    "void_policy": draft.void_policy,
    "settlement_source_id": public_id("SRC", draft.settlement_source_id),
    "discovery_source_id": public_id("SRC", draft.discovery_source_id),
    "status": draft.status,
    "checks": draft.checks_json,
    "risk_flags": draft.risk_flags_json,
    "ai_rationale": draft.ai_rationale,
    "confidence_score": draft.confidence_score,
    "admin_notes": draft.admin_notes,
    "evidence": [evidence_to_response(item) for item in draft.evidence],
    "created_at": draft.created_at,
    "updated_at": draft.updated_at,
  }


def list_sources(db: Session, *, category_slug: str | None = None, limit: int = 100) -> list[DataSource]:
  stmt = select(DataSource).order_by(DataSource.category_slug.asc(), DataSource.name.asc()).limit(limit)
  if category_slug:
    stmt = stmt.where(DataSource.category_slug == category_slug)
  return list(db.scalars(stmt).all())


def create_source(db: Session, *, payload, admin: User, request_id: str | None) -> DataSource:
  if not db.get(Category, payload.category_slug):
    raise AppError(422, "CATEGORY_NOT_APPROVED", "Data source category is not approved.")
  source = DataSource(
    name=payload.name.strip(),
    provider=payload.provider.strip(),
    source_type=payload.source_type.strip().upper(),
    category_slug=payload.category_slug,
    base_url=payload.base_url.strip(),
    license_status=payload.license_status.strip().upper(),
    automation_level=payload.automation_level,
    refresh_schedule=payload.refresh_schedule.strip().upper(),
    settlement_eligible=payload.settlement_eligible,
    discovery_eligible=payload.discovery_eligible,
    status=payload.status.strip().upper(),
    config_json=payload.config,
    notes=payload.notes,
  )
  db.add(source)
  try:
    db.flush()
  except IntegrityError as exc:
    raise AppError(409, "DATA_SOURCE_EXISTS", "A data source with this name and provider already exists.") from exc
  write_audit_log(
    db,
    event_type="DATA_SOURCE_CREATED",
    actor_user_id=admin.id,
    request_id=request_id,
    metadata={"source_id": source.id, "category_slug": source.category_slug, "settlement_eligible": source.settlement_eligible},
  )
  return source


def test_source(db: Session, *, source_id: str, admin: User, request_id: str | None) -> DataSource:
  source = get_source_or_404(db, source_id)
  source.health_status = "PASS" if source.status == "ACTIVE" and source.base_url else "FAIL"
  source.last_checked_at = utc_now()
  write_audit_log(
    db,
    event_type="DATA_SOURCE_TESTED",
    actor_user_id=admin.id,
    request_id=request_id,
    metadata={"source_id": source.id, "health_status": source.health_status},
  )
  return source


def list_events(db: Session, *, category_slug: str | None = None, limit: int = 100) -> list[SourceEvent]:
  stmt = select(SourceEvent).order_by(SourceEvent.ingested_at.desc()).limit(limit)
  if category_slug:
    stmt = stmt.where(SourceEvent.category_slug == category_slug)
  return list(db.scalars(stmt).all())


def run_ingestion(db: Session, *, payload, admin: User, request_id: str | None) -> tuple[list[SourceEvent], int]:
  sources = _sources_for_ingestion(db, source_id=payload.source_id, category_slug=payload.category_slug)
  created: list[SourceEvent] = []
  skipped = 0
  for source in sources[: payload.limit]:
    title = _ingestion_title(source, payload.query)
    event = create_source_event(
      db,
      source=source,
      title=title,
      url=source.base_url,
      raw_payload={
        "provider": source.provider,
        "query": payload.query,
        "generated_by": "LOCAL_INGESTION_RUN",
        "source_type": source.source_type,
      },
    )
    if event:
      created.append(event)
    else:
      skipped += 1
  write_audit_log(
    db,
    event_type="SOURCE_INGESTION_RUN",
    actor_user_id=admin.id,
    request_id=request_id,
    metadata={"created_events": len(created), "skipped_duplicates": skipped, "source_count": len(sources)},
  )
  return created, skipped


def create_source_event(db: Session, *, source: DataSource, title: str, url: str | None, raw_payload: dict[str, Any]) -> SourceEvent | None:
  now = utc_now()
  normalized = f"{source.id}:{title.strip().lower()}:{url or source.base_url}"
  content_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
  dedupe_key = content_hash[:32]
  duplicate = db.scalar(select(SourceEvent.id).where(SourceEvent.data_source_id == source.id, SourceEvent.dedupe_key == dedupe_key))
  if duplicate:
    return None
  event = SourceEvent(
    data_source_id=source.id,
    category_slug=source.category_slug,
    external_id=raw_payload.get("external_id"),
    title=title.strip(),
    url=url,
    published_at=now,
    source_timestamp=now,
    raw_payload_json=raw_payload,
    content_hash=content_hash,
    dedupe_key=dedupe_key,
    credibility_score=85 if source.settlement_eligible else 70,
  )
  db.add(event)
  db.flush()
  return event


def list_drafts(db: Session, *, status: str | None = None, origin: str | None = None, limit: int = 100) -> list[MarketDraft]:
  stmt = select(MarketDraft).options(selectinload(MarketDraft.evidence)).order_by(MarketDraft.created_at.desc()).limit(limit)
  if status:
    stmt = stmt.where(MarketDraft.status == status.upper())
  if origin:
    stmt = stmt.where(MarketDraft.origin == origin.upper())
  return list(db.scalars(stmt).all())


def create_draft(db: Session, *, payload, admin: User | None, request_id: str | None) -> MarketDraft:
  origin = payload.origin.upper()
  if origin not in {"AI", "ADMIN", "TRADER"}:
    raise AppError(422, "INVALID_DRAFT_ORIGIN", "Market draft origin is not supported.")
  if origin != "ADMIN" and payload.list_immediately:
    raise AppError(422, "INVALID_DRAFT_ACTION", "Only admin-created drafts can be listed immediately.")
  checks, risk_flags = run_draft_checks(
    db,
    category_slug=payload.category_slug,
    market_type=payload.market_type,
    question=payload.question,
    outcomes=payload.outcomes,
    source=payload.source,
    resolution_rule=payload.resolution_rule,
    void_policy=payload.void_policy,
    close_time=payload.close_time,
    origin=origin,
    settlement_source_id=_resolve_source_id(db, payload.settlement_source_id) if payload.settlement_source_id else None,
    discovery_source_id=_resolve_source_id(db, payload.discovery_source_id) if payload.discovery_source_id else None,
    ai_rationale=payload.ai_rationale,
    confidence_score=payload.confidence_score,
  )
  passed = all(item["passed"] for item in checks.values())
  status = "APPROVED" if origin == "ADMIN" and passed else "NEEDS_REVIEW" if passed else "NEEDS_CHANGES"
  draft = MarketDraft(
    origin=origin,
    created_by_user_id=admin.id if admin else None,
    category_slug=payload.category_slug,
    subcategory=payload.subcategory.strip() or "General",
    market_type=payload.market_type,
    question=payload.question.strip(),
    outcomes_json=[item.strip() for item in payload.outcomes if item.strip()],
    close_time=payload.close_time.strip(),
    source=payload.source.strip(),
    resolution_rule=payload.resolution_rule.strip(),
    void_policy=payload.void_policy.strip(),
    settlement_source_id=_resolve_source_id(db, payload.settlement_source_id) if payload.settlement_source_id else None,
    discovery_source_id=_resolve_source_id(db, payload.discovery_source_id) if payload.discovery_source_id else None,
    status=status,
    checks_json=checks,
    risk_flags_json=risk_flags,
    ai_rationale=payload.ai_rationale,
    confidence_score=payload.confidence_score,
    admin_notes=payload.admin_notes,
  )
  db.add(draft)
  db.flush()
  _create_review_for_draft(db, draft=draft, submitted_by=admin.email if admin else origin)
  write_audit_log(
    db,
    event_type="MARKET_DRAFT_CREATED",
    actor_user_id=admin.id if admin else None,
    request_id=request_id,
    metadata={"draft_id": draft.id, "origin": draft.origin, "status": draft.status},
  )
  write_admin_event(db, event_type="admin.market_draft.created", suffix="review_queue", payload={"draft_id": draft.id, "origin": draft.origin, "status": draft.status})
  if payload.list_immediately and draft.status == "APPROVED":
    list_draft(db, draft_id=draft.id, admin=admin, request_id=request_id)
  return draft


def create_trader_draft_from_suggestion(db: Session, *, suggestion, user: User, request_id: str | None) -> MarketDraft:
  checks, risk_flags = run_draft_checks(
    db,
    category_slug=suggestion.category_slug,
    market_type=suggestion.market_type,
    question=suggestion.question,
    outcomes=suggestion.outcomes_json,
    source=suggestion.source,
    resolution_rule=suggestion.resolution_rule,
    void_policy="Void only if approved source is unavailable or category rulebook requires voiding.",
    close_time="Admin must set close time",
    origin="TRADER",
    settlement_source_id=None,
    discovery_source_id=None,
    ai_rationale=None,
    confidence_score=None,
  )
  passed = all(item["passed"] for item in checks.values())
  draft = MarketDraft(
    origin="TRADER",
    created_by_user_id=user.id,
    suggestion_id=suggestion.id,
    category_slug=suggestion.category_slug,
    subcategory="User suggestion",
    market_type=suggestion.market_type,
    question=suggestion.question,
    outcomes_json=suggestion.outcomes_json,
    close_time="Admin must set close time",
    source=suggestion.source,
    resolution_rule=suggestion.resolution_rule,
    void_policy="Void only if approved source is unavailable or category rulebook requires voiding.",
    status="NEEDS_REVIEW" if passed else "NEEDS_CHANGES",
    checks_json=checks,
    risk_flags_json=risk_flags,
  )
  db.add(draft)
  db.flush()
  _create_review_for_draft(db, draft=draft, submitted_by=user.email, suggestion_id=suggestion.id)
  write_audit_log(
    db,
    event_type="MARKET_DRAFT_CREATED_FROM_SUGGESTION",
    actor_user_id=user.id,
    target_user_id=user.id,
    request_id=request_id,
    metadata={"draft_id": draft.id, "suggestion_id": suggestion.id, "status": draft.status},
  )
  return draft


def update_draft(db: Session, *, draft_id: str, payload, admin: User, request_id: str | None) -> MarketDraft:
  draft = get_draft_or_404(db, draft_id)
  if draft.status in TERMINAL_DRAFT_STATUSES:
    raise AppError(409, "DRAFT_LOCKED", "Terminal market drafts cannot be edited.")
  updates = payload.model_dump(exclude_unset=True)
  if "outcomes" in updates:
    draft.outcomes_json = [item.strip() for item in updates.pop("outcomes") if item.strip()]
  if "settlement_source_id" in updates and updates["settlement_source_id"]:
    updates["settlement_source_id"] = _resolve_source_id(db, updates["settlement_source_id"])
  if "discovery_source_id" in updates and updates["discovery_source_id"]:
    updates["discovery_source_id"] = _resolve_source_id(db, updates["discovery_source_id"])
  for key, value in updates.items():
    if key in {"source", "resolution_rule", "void_policy", "question", "subcategory"} and isinstance(value, str):
      value = value.strip()
    setattr(draft, key, value)
  checks, risk_flags = run_draft_checks(
    db,
    category_slug=draft.category_slug,
    market_type=draft.market_type,
    question=draft.question,
    outcomes=draft.outcomes_json,
    source=draft.source,
    resolution_rule=draft.resolution_rule,
    void_policy=draft.void_policy,
    close_time=draft.close_time,
    origin=draft.origin,
    settlement_source_id=draft.settlement_source_id,
    discovery_source_id=draft.discovery_source_id,
    ai_rationale=draft.ai_rationale,
    confidence_score=draft.confidence_score,
    exclude_draft_id=draft.id,
  )
  draft.checks_json = checks
  draft.risk_flags_json = risk_flags
  if draft.status == "NEEDS_CHANGES" and all(item["passed"] for item in checks.values()):
    draft.status = "NEEDS_REVIEW"
  write_audit_log(
    db,
    event_type="MARKET_DRAFT_UPDATED",
    actor_user_id=admin.id,
    request_id=request_id,
    metadata={"draft_id": draft.id, "status": draft.status},
  )
  return draft


def approve_draft(db: Session, *, draft_id: str, admin: User, request_id: str | None) -> MarketDraft:
  draft = get_draft_or_404(db, draft_id)
  if draft.status in TERMINAL_DRAFT_STATUSES:
    raise AppError(409, "DRAFT_LOCKED", "Terminal market drafts cannot be approved.")
  checks, risk_flags = run_draft_checks(
    db,
    category_slug=draft.category_slug,
    market_type=draft.market_type,
    question=draft.question,
    outcomes=draft.outcomes_json,
    source=draft.source,
    resolution_rule=draft.resolution_rule,
    void_policy=draft.void_policy,
    close_time=draft.close_time,
    origin=draft.origin,
    settlement_source_id=draft.settlement_source_id,
    discovery_source_id=draft.discovery_source_id,
    ai_rationale=draft.ai_rationale,
    confidence_score=draft.confidence_score,
    exclude_draft_id=draft.id,
  )
  draft.checks_json = checks
  draft.risk_flags_json = risk_flags
  if not all(item["passed"] for item in checks.values()):
    draft.status = "NEEDS_CHANGES"
    raise AppError(422, "DRAFT_CHECKS_FAILED", "Market draft cannot be approved until all checks pass.", checks)
  draft.status = "APPROVED"
  _resolve_review(db, draft=draft, status="Approved")
  write_audit_log(
    db,
    event_type="MARKET_DRAFT_APPROVED",
    actor_user_id=admin.id,
    request_id=request_id,
    metadata={"draft_id": draft.id, "origin": draft.origin},
  )
  write_admin_event(db, event_type="admin.market_draft.approved", suffix="review_queue", payload={"draft_id": draft.id, "status": draft.status})
  return draft


def reject_draft(db: Session, *, draft_id: str, admin: User, request_id: str | None, reason: str | None = None) -> MarketDraft:
  draft = get_draft_or_404(db, draft_id)
  if draft.status == "LISTED":
    raise AppError(409, "DRAFT_ALREADY_LISTED", "Listed market drafts cannot be rejected.")
  draft.status = "REJECTED"
  draft.admin_notes = reason or draft.admin_notes
  _resolve_review(db, draft=draft, status="Rejected")
  write_audit_log(
    db,
    event_type="MARKET_DRAFT_REJECTED",
    actor_user_id=admin.id,
    request_id=request_id,
    metadata={"draft_id": draft.id, "reason": reason},
  )
  write_admin_event(db, event_type="admin.market_draft.rejected", suffix="review_queue", payload={"draft_id": draft.id, "status": draft.status})
  return draft


def list_draft(db: Session, *, draft_id: str, admin: User | None, request_id: str | None) -> MarketDraft:
  draft = get_draft_or_404(db, draft_id)
  if draft.status != "APPROVED":
    raise AppError(409, "DRAFT_NOT_APPROVED", "Only approved market drafts can be listed.")
  if draft.listed_market_id:
    raise AppError(409, "DRAFT_ALREADY_LISTED", "Market draft is already listed.")
  market_id = unique_market_id(db, draft.question)
  probability = 50
  outcomes = draft.outcomes_json or ["YES", "NO"]
  market = Market(
    id=market_id,
    title=draft.question,
    category_slug=draft.category_slug,
    subcategory=draft.subcategory,
    market_type=draft.market_type,
    status="OPEN",
    close_time=draft.close_time,
    source=draft.source,
    rule_summary=draft.resolution_rule,
    probability=probability,
    change_24h=0,
    volume_24h=0,
    total_volume=0,
    liquidity=0,
    spread=0,
    traders=0,
    risk_notes_json=draft.risk_flags_json,
    price_history_json=[],
    order_book_json={"yes_bids": [], "no_bids": []},
    recent_trades_json=[],
  )
  db.add(market)
  db.flush()
  db.add(
    MarketRule(
      market_id=market.id,
      resolution_rule=draft.resolution_rule,
      void_policy=draft.void_policy,
      source_url=_source_url(db, draft.settlement_source_id),
    )
  )
  for outcome in outcomes:
    market.outcomes.append(Outcome(label=outcome, price=probability if outcome.upper() == "YES" else 100 - probability, probability=probability if outcome.upper() == "YES" else 100 - probability))
  db.add(
    OracleEvidence(
      market_id=market.id,
      source_name=draft.source,
      source_url=_source_url(db, draft.settlement_source_id),
      captured_payload_json={"draft_id": draft.id, "evidence": [evidence.snapshot_json for evidence in draft.evidence]},
    )
  )
  draft.listed_market_id = market.id
  draft.status = "LISTED"
  _resolve_review(db, draft=draft, status="Listed")
  write_audit_log(
    db,
    event_type="MARKET_DRAFT_LISTED",
    actor_user_id=admin.id if admin else None,
    request_id=request_id,
    metadata={"draft_id": draft.id, "market_id": market.id, "origin": draft.origin},
  )
  write_market_event(db, event_type="market.status_changed", market_id=market.id, suffix="status", payload={"market_id": market.id, "status": market.status})
  write_admin_event(db, event_type="admin.market_draft.listed", suffix="review_queue", market_id=market.id, payload={"draft_id": draft.id, "market_id": market.id, "status": draft.status})
  return draft


def generate_ai_drafts(db: Session, *, payload, admin: User, request_id: str | None) -> list[MarketDraft]:
  events = _events_for_ai_generation(db, source_event_id=payload.source_event_id, category_slug=payload.category_slug, limit=payload.limit)
  drafts: list[MarketDraft] = []
  for event in events:
    source = event.data_source
    question = _ai_question_from_event(event)
    existing = db.scalar(select(MarketDraft.id).where(func.lower(MarketDraft.question) == question.lower()))
    if existing:
      continue
    checks, risk_flags = run_draft_checks(
      db,
      category_slug=event.category_slug,
      market_type="Binary",
      question=question,
      outcomes=["YES", "NO"],
      source=source.name,
      resolution_rule=f"YES resolves if {source.name} confirms the event described by the market question before the stated deadline. Otherwise NO resolves, unless the void policy applies.",
      void_policy="Void only if the named approved source is unavailable or the admin rulebook determines the source event was invalid.",
      close_time="Admin must set close time",
      origin="AI",
      settlement_source_id=source.id if source.settlement_eligible else None,
      discovery_source_id=source.id,
      ai_rationale=f"Candidate generated from source event: {event.title}",
      confidence_score=78,
    )
    draft = MarketDraft(
      origin="AI",
      created_by_user_id=admin.id,
      category_slug=event.category_slug,
      subcategory="AI candidate",
      market_type="Binary",
      question=question,
      outcomes_json=["YES", "NO"],
      close_time="Admin must set close time",
      source=source.name,
      resolution_rule=f"YES resolves if {source.name} confirms the event described by the market question before the stated deadline. Otherwise NO resolves, unless the void policy applies.",
      void_policy="Void only if the named approved source is unavailable or the admin rulebook determines the source event was invalid.",
      settlement_source_id=source.id if source.settlement_eligible else None,
      discovery_source_id=source.id,
      status="NEEDS_REVIEW" if all(item["passed"] for item in checks.values()) else "NEEDS_CHANGES",
      checks_json=checks,
      risk_flags_json=risk_flags,
      ai_rationale=f"Candidate generated from source event: {event.title}",
      confidence_score=78,
    )
    db.add(draft)
    db.flush()
    draft.evidence.append(
      MarketDraftEvidence(
        source_event_id=event.id,
        data_source_id=source.id,
        title=event.title,
        url=event.url,
        evidence_type="SOURCE_EVENT",
        snapshot_json={"event_id": event.id, "content_hash": event.content_hash, "raw_payload": event.raw_payload_json},
      )
    )
    _create_review_for_draft(db, draft=draft, submitted_by="AI generator")
    write_audit_log(
      db,
      event_type="AI_MARKET_DRAFT_CREATED",
      actor_user_id=admin.id,
      request_id=request_id,
      metadata={"draft_id": draft.id, "source_event_id": event.id, "status": draft.status},
    )
    drafts.append(draft)
  write_admin_event(db, event_type="admin.ai_market_generation.completed", suffix="review_queue", payload={"created_drafts": len(drafts)})
  return drafts


def run_draft_checks(
  db: Session,
  *,
  category_slug: str,
  market_type: str,
  question: str,
  outcomes: list[str],
  source: str,
  resolution_rule: str,
  void_policy: str,
  close_time: str,
  origin: str,
  settlement_source_id: str | None,
  discovery_source_id: str | None,
  ai_rationale: str | None,
  confidence_score: int | None,
  exclude_draft_id: str | None = None,
) -> tuple[dict[str, dict[str, bool | str]], list[str]]:
  category = db.get(Category, category_slug)
  duplicate_market = db.scalar(select(Market.id).where(func.lower(Market.title) == question.strip().lower()))
  duplicate_draft_query = select(MarketDraft.id).where(
    func.lower(MarketDraft.question) == question.strip().lower(),
    MarketDraft.status.notin_(["REJECTED", "ARCHIVED"]),
  )
  if exclude_draft_id:
    duplicate_draft_query = duplicate_draft_query.where(MarketDraft.id != exclude_draft_id)
  duplicate_draft = db.scalar(duplicate_draft_query)
  lower_text = f"{question} {resolution_rule}".lower()
  prohibited_hit = next((term for term in PROHIBITED_TERMS if term in lower_text), None)
  cleaned_outcomes = [item.strip() for item in outcomes if item.strip()]
  settlement_source = db.get(DataSource, settlement_source_id) if settlement_source_id else None
  discovery_source = db.get(DataSource, discovery_source_id) if discovery_source_id else None
  settlement_source_ok = bool(
    settlement_source
    and settlement_source.status == "ACTIVE"
    and settlement_source.settlement_eligible
    and settlement_source.license_status in {"APPROVED", "PUBLIC_OFFICIAL", "LICENSED"}
  )
  discovery_source_ok = origin != "AI" or bool(discovery_source and discovery_source.status == "ACTIVE" and discovery_source.discovery_eligible)
  ai_context_ok = origin != "AI" or bool(ai_rationale and confidence_score is not None)

  checks: dict[str, dict[str, bool | str]] = {
    "category_allowed": {"passed": category is not None, "detail": "Category exists." if category else "Category is not approved."},
    "market_type_allowed": {"passed": market_type in ALLOWED_MARKET_TYPES, "detail": "Market type is supported." if market_type in ALLOWED_MARKET_TYPES else "Market type is not supported."},
    "source_present": {"passed": bool(source.strip()), "detail": "Source supplied." if source.strip() else "Source is required."},
    "settlement_source_approved": {"passed": settlement_source_ok, "detail": "Settlement source is active and approved." if settlement_source_ok else "Approved settlement source is required before listing."},
    "discovery_source_valid": {"passed": discovery_source_ok, "detail": "Discovery source is valid." if discovery_source_ok else "AI drafts require an approved discovery source."},
    "duplicate_title": {"passed": duplicate_market is None and duplicate_draft is None, "detail": "No exact duplicate found." if duplicate_market is None and duplicate_draft is None else "Exact market or draft title already exists."},
    "prohibited_topic": {"passed": prohibited_hit is None, "detail": "No prohibited keyword hit." if prohibited_hit is None else f"Matched prohibited keyword: {prohibited_hit}."},
    "close_time_valid": {"passed": bool(close_time.strip()) and "admin must set" not in close_time.strip().lower(), "detail": "Close time supplied." if close_time.strip() and "admin must set" not in close_time.strip().lower() else "Final close time must be set before approval/listing."},
    "outcomes_valid": {"passed": len(cleaned_outcomes) >= 2 and len(set(cleaned_outcomes)) == len(cleaned_outcomes), "detail": "At least two unique outcomes supplied."},
    "resolution_rule_present": {"passed": bool(resolution_rule.strip()), "detail": "Resolution rule supplied." if resolution_rule.strip() else "Resolution rule is required."},
    "void_policy_present": {"passed": bool(void_policy.strip()), "detail": "Void policy supplied." if void_policy.strip() else "Void policy is required."},
    "risk_category_assigned": {"passed": category is not None, "detail": f"Risk is {category.risk}." if category else "No category risk available."},
    "source_license_acceptable": {"passed": settlement_source_ok, "detail": "Source license is acceptable for settlement." if settlement_source_ok else "Source license is not approved for settlement."},
    "ai_rationale_present": {"passed": ai_context_ok, "detail": "AI rationale and confidence supplied." if ai_context_ok else "AI drafts require rationale and confidence."},
  }

  risk_flags: list[str] = []
  if category_slug in RESTRICTED_CATEGORIES:
    risk_flags.append("Category requires stricter legal/data review before real-money launch.")
  if prohibited_hit:
    risk_flags.append(f"Prohibited topic keyword matched: {prohibited_hit}.")
  if not settlement_source_ok:
    risk_flags.append("No approved settlement source is attached.")
  if duplicate_market or duplicate_draft:
    risk_flags.append("Potential exact duplicate detected.")
  return checks, risk_flags


def get_source_or_404(db: Session, source_id: str) -> DataSource:
  internal_id = _resolve_source_id(db, source_id)
  source = db.get(DataSource, internal_id)
  if not source:
    raise AppError(404, "DATA_SOURCE_NOT_FOUND", "Data source was not found.")
  return source


def get_draft_or_404(db: Session, draft_id: str) -> MarketDraft:
  draft = db.scalar(select(MarketDraft).where(MarketDraft.id == draft_id).options(selectinload(MarketDraft.evidence)))
  if not draft:
    for candidate in db.scalars(select(MarketDraft).options(selectinload(MarketDraft.evidence))).all():
      if matches_public_id("DRF", candidate.id, draft_id):
        draft = candidate
        break
  if not draft:
    raise AppError(404, "MARKET_DRAFT_NOT_FOUND", "Market draft was not found.")
  return draft


def unique_market_id(db: Session, title: str) -> str:
  base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:80] or "market"
  candidate = base
  index = 2
  while db.get(Market, candidate):
    candidate = f"{base}-{index}"
    index += 1
  return candidate


def _resolve_source_id(db: Session, source_id: str) -> str:
  if db.get(DataSource, source_id):
    return source_id
  for candidate in db.scalars(select(DataSource)).all():
    if matches_public_id("SRC", candidate.id, source_id):
      return candidate.id
  raise AppError(404, "DATA_SOURCE_NOT_FOUND", "Data source was not found.")


def _sources_for_ingestion(db: Session, *, source_id: str | None, category_slug: str | None) -> list[DataSource]:
  stmt = select(DataSource).where(DataSource.status == "ACTIVE", DataSource.discovery_eligible.is_(True)).order_by(DataSource.category_slug.asc(), DataSource.name.asc())
  if source_id:
    stmt = stmt.where(DataSource.id == _resolve_source_id(db, source_id))
  if category_slug:
    stmt = stmt.where(DataSource.category_slug == category_slug)
  sources = list(db.scalars(stmt).all())
  if not sources:
    raise AppError(404, "NO_DISCOVERY_SOURCES", "No active discovery sources matched the ingestion request.")
  return sources


def _events_for_ai_generation(db: Session, *, source_event_id: str | None, category_slug: str | None, limit: int) -> list[SourceEvent]:
  stmt = select(SourceEvent).options(selectinload(SourceEvent.data_source)).order_by(SourceEvent.ingested_at.desc()).limit(limit)
  if source_event_id:
    internal_id = source_event_id
    if not db.get(SourceEvent, internal_id):
      for candidate in db.scalars(select(SourceEvent)).all():
        if matches_public_id("EVS", candidate.id, source_event_id):
          internal_id = candidate.id
          break
    stmt = stmt.where(SourceEvent.id == internal_id)
  if category_slug:
    stmt = stmt.where(SourceEvent.category_slug == category_slug)
  events = list(db.scalars(stmt).all())
  if not events:
    raise AppError(404, "NO_SOURCE_EVENTS", "No source events are available for AI market generation.")
  return events


def _ingestion_title(source: DataSource, query: str | None) -> str:
  subject = query.strip() if query else source.config_json.get("default_query") or source.name
  templates = {
    "sports": f"Official schedule/result watch: {subject}",
    "economics": f"Upcoming official economic release: {subject}",
    "weather-climate": f"Official weather observation watch: {subject}",
    "commodities": f"Official commodity benchmark watch: {subject}",
    "tech-science": f"Official technology/science announcement watch: {subject}",
  }
  return templates.get(source.category_slug, f"Approved source watch: {subject}")


def _ai_question_from_event(event: SourceEvent) -> str:
  category = event.category_slug
  title = event.title.rstrip(".?")
  if category == "economics":
    return f"Will the official release described by '{title}' exceed the admin-defined threshold?"
  if category == "weather-climate":
    return f"Will the official weather event described by '{title}' meet the admin-defined threshold?"
  if category == "commodities":
    return f"Will the official benchmark described by '{title}' settle above the admin-defined threshold?"
  if category == "sports":
    return f"Will the event described by '{title}' resolve YES under the official source?"
  return f"Will the event described by '{title}' occur by the admin-defined deadline?"


def _create_review_for_draft(db: Session, *, draft: MarketDraft, submitted_by: str, suggestion_id: str | None = None) -> AdminReview:
  category = db.get(Category, draft.category_slug)
  review = AdminReview(
    suggestion_id=suggestion_id or draft.suggestion_id,
    market_id=draft.listed_market_id,
    draft_id=draft.id,
    title=draft.question,
    category=category.name if category else draft.category_slug,
    status=_review_status(draft),
    risk=category.risk if category else "HIGH",
    submitted_by=submitted_by,
  )
  db.add(review)
  return review


def _review_status(draft: MarketDraft) -> str:
  if draft.status == "NEEDS_CHANGES":
    return "Needs changes"
  if draft.status == "APPROVED":
    return "Approved"
  if draft.status == "LISTED":
    return "Listed"
  if draft.origin == "AI":
    return "AI candidate"
  if draft.origin == "TRADER":
    return "Trader suggestion"
  return "Direct create review"


def _resolve_review(db: Session, *, draft: MarketDraft, status: str) -> None:
  review = db.scalar(select(AdminReview).where(AdminReview.draft_id == draft.id).order_by(AdminReview.created_at.desc()))
  if review:
    review.status = status
    review.market_id = draft.listed_market_id
    review.resolved_at = utc_now() if status in {"Approved", "Rejected", "Listed"} else None


def _source_url(db: Session, source_id: str | None) -> str | None:
  if not source_id:
    return None
  source = db.get(DataSource, source_id)
  return source.base_url if source else None
