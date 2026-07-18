from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.public_ids import matches_public_id, public_id
from app.core.security import utc_now
from app.modules.admin.models import AdminReview
from app.modules.audit.service import write_audit_log
from app.modules.markets.models import Market
from app.modules.realtime.service import write_admin_event, write_market_event
from app.modules.users.models import User


def review_to_response(review: AdminReview) -> dict:
  return {
    "id": public_id("REV", review.id),
    "suggestion_id": public_id("SUG", review.suggestion_id),
    "draft_id": public_id("DRF", review.draft_id),
    "market_id": review.market_id,
    "title": review.title,
    "category": review.category,
    "status": review.status,
    "risk": review.risk,
    "submitted_by": review.submitted_by,
    "created_at": review.created_at,
    "resolved_at": review.resolved_at,
  }


def list_reviews(db: Session, *, limit: int) -> list[AdminReview]:
  return list(db.scalars(select(AdminReview).order_by(AdminReview.created_at.desc()).limit(limit)).all())


def get_review_or_404(db: Session, *, review_id: str) -> AdminReview:
  review = db.get(AdminReview, review_id)
  if not review:
    for candidate in db.scalars(select(AdminReview)).all():
      if matches_public_id("REV", candidate.id, review_id):
        review = candidate
        break
  if not review:
    raise AppError(404, "ADMIN_REVIEW_NOT_FOUND", "Admin review was not found.")
  return review


def set_market_status(db: Session, *, market_id: str, status: str, admin: User, request_id: str | None) -> Market:
  market = db.get(Market, market_id)
  if not market:
    raise AppError(404, "MARKET_NOT_FOUND", "Market was not found.")
  market.status = status
  market.updated_at = utc_now()
  write_audit_log(
    db,
    event_type=f"MARKET_{status}",
    actor_user_id=admin.id,
    request_id=request_id,
    metadata={"market_id": market.id, "status": status},
  )
  write_market_event(db, event_type="market.status_changed", market_id=market.id, suffix="status", payload={"market_id": market.id, "status": status})
  write_admin_event(db, event_type="admin.review_queue.updated", suffix="review_queue", market_id=market.id, payload={"market_id": market.id, "status": status})
  return market
