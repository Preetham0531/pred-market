from sqlalchemy import func, select
from sqlalchemy.orm import Session, object_session

from app.core.errors import AppError
from app.core.public_ids import matches_public_id, public_id
from app.modules.audit.service import write_audit_log
from app.modules.market_suggestions.models import MarketSuggestion
from app.modules.markets.models import Category, Market
from app.modules.market_issuance.models import MarketDraft
from app.modules.market_issuance.service import create_trader_draft_from_suggestion
from app.modules.users.models import User

PROHIBITED_TERMS = {"death", "assassination", "terror", "violence", "personal health"}
ALLOWED_MARKET_TYPES = {"Binary", "Multiple-choice", "Range", "Threshold", "Conditional", "Combo"}


def run_suggestion_checks(db: Session, payload) -> dict[str, dict[str, bool | str]]:
  duplicate = db.scalar(select(Market.id).where(func.lower(Market.title) == payload.question.strip().lower()))
  category = db.get(Category, payload.category_slug)
  lower_text = f"{payload.question} {payload.resolution_rule}".lower()
  prohibited_hit = next((term for term in PROHIBITED_TERMS if term in lower_text), None)

  return {
    "duplicate_title": {"passed": duplicate is None, "detail": "No exact duplicate found." if duplicate is None else "Exact market title already exists."},
    "category_allowed": {"passed": category is not None, "detail": "Category exists." if category else "Category is not approved."},
    "source_present": {"passed": bool(payload.source.strip()), "detail": "Source supplied."},
    "prohibited_topic": {"passed": prohibited_hit is None, "detail": "No prohibited keyword hit." if prohibited_hit is None else f"Matched prohibited keyword: {prohibited_hit}."},
    "resolution_rule_present": {"passed": bool(payload.resolution_rule.strip()), "detail": "Resolution rule supplied."},
  }


def suggestion_to_response(suggestion: MarketSuggestion) -> dict:
  draft = None
  session = object_session(suggestion)
  if suggestion.id and session:
    draft = session.scalar(select(MarketDraft).where(MarketDraft.suggestion_id == suggestion.id))
  return {
    "id": public_id("SUG", suggestion.id),
    "draft_id": public_id("DRF", draft.id) if draft else None,
    "submitted_by_user_id": public_id("USR", suggestion.submitted_by_user_id),
    "category_slug": suggestion.category_slug,
    "market_type": suggestion.market_type,
    "question": suggestion.question,
    "outcomes": suggestion.outcomes_json,
    "source": suggestion.source,
    "resolution_rule": suggestion.resolution_rule,
    "status": suggestion.status,
    "checks": suggestion.checks_json,
    "created_at": suggestion.created_at,
    "updated_at": suggestion.updated_at,
  }


def create_suggestion(db: Session, *, payload, user: User, request_id: str | None) -> MarketSuggestion:
  if payload.market_type not in ALLOWED_MARKET_TYPES:
    raise AppError(422, "INVALID_MARKET_TYPE", "Market type is not supported for V1.")
  checks = run_suggestion_checks(db, payload)
  status = "PENDING_REVIEW" if all(item["passed"] for item in checks.values()) else "NEEDS_CHANGES"
  suggestion = MarketSuggestion(
    submitted_by_user_id=user.id,
    category_slug=payload.category_slug,
    market_type=payload.market_type,
    question=payload.question.strip(),
    outcomes_json=payload.outcomes,
    source=payload.source.strip(),
    resolution_rule=payload.resolution_rule.strip(),
    status=status,
    checks_json=checks,
  )
  db.add(suggestion)
  db.flush()
  draft = create_trader_draft_from_suggestion(db, suggestion=suggestion, user=user, request_id=request_id)
  suggestion.status = draft.status
  suggestion.checks_json = draft.checks_json
  write_audit_log(
    db,
    event_type="MARKET_SUGGESTION_CREATED",
    actor_user_id=user.id,
    target_user_id=user.id,
    request_id=request_id,
    metadata={"suggestion_id": suggestion.id, "status": status},
  )
  return suggestion


def get_suggestion_or_404(db: Session, suggestion_id: str, user: User) -> MarketSuggestion:
  suggestion = db.get(MarketSuggestion, suggestion_id)
  if not suggestion:
    for candidate in db.scalars(select(MarketSuggestion)).all():
      if matches_public_id("SUG", candidate.id, suggestion_id):
        suggestion = candidate
        break
  if not suggestion:
    raise AppError(404, "SUGGESTION_NOT_FOUND", "Market suggestion was not found.")
  roles = {role.role for role in user.roles}
  if suggestion.submitted_by_user_id != user.id and "ADMIN" not in roles:
    raise AppError(403, "FORBIDDEN", "You do not have permission to view this suggestion.")
  return suggestion
