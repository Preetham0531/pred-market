from fastapi import APIRouter, Depends, Header, Query, Request, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rate_limit import check_rate_limit
from app.db.session import get_db
from app.modules.admin.schemas import (
  AdminActionResponse,
  AdminReviewList,
  AdminReviewResponse,
  AdminUserList,
  ImpersonationAuthResponse,
  ImpersonationStartRequest,
)
from app.modules.admin.service import get_review_or_404, list_reviews, review_to_response, set_market_status
from app.modules.analytics.schemas import RecomputeResponse
from app.modules.analytics.service import recompute_all
from app.modules.auth.dependencies import AuthContext, get_auth_context, require_admin, require_checker
from app.modules.auth.router import request_meta
from app.modules.auth.service import auth_me_response, list_admin_switchable_users, start_impersonation, stop_impersonation, user_to_response
from app.modules.market_issuance.schemas import (
  AIMarketGenerationRunRequest,
  AIMarketGenerationRunResponse,
  DataSourceCreate,
  DataSourceList,
  DataSourceResponse,
  DataSourceTestResponse,
  IngestionRunCreate,
  IngestionRunResponse,
  MarketDraftActionResponse,
  MarketDraftCreate,
  MarketDraftList,
  MarketDraftPatch,
  MarketDraftResponse,
  SourceEventList,
)
from app.modules.market_issuance.service import (
  approve_draft,
  create_draft,
  create_source,
  draft_to_response,
  event_to_response,
  generate_ai_drafts,
  get_draft_or_404,
  list_drafts,
  list_events,
  list_sources,
  list_draft,
  run_ingestion,
  source_to_response,
  test_source,
  update_draft,
  reject_draft,
)
from app.modules.realtime.service import publish_pending_events
from app.modules.settlement.schemas import EvidenceCreate, EvidenceResponse, ResolutionProposalCreate, ResolutionProposalResponse, SettlementResponse
from app.modules.settlement.service import (
  add_evidence,
  approve_resolution_proposal,
  close_market,
  create_resolution_proposal,
  evidence_to_response,
  proposal_to_response,
  settle_market,
  settlement_to_response,
)
from app.modules.users.models import User

router = APIRouter()


@router.get("/users", response_model=AdminUserList)
def admin_users_endpoint(
  q: str | None = Query(default=None, min_length=1, max_length=120),
  limit: int = Query(default=20, ge=1, le=50),
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  _ = admin
  users = list_admin_switchable_users(db, query=q, limit=limit)
  return {"items": [user_to_response(user) for user in users], "next_cursor": None}


@router.post("/impersonation/start", response_model=ImpersonationAuthResponse)
def admin_start_impersonation_endpoint(
  payload: ImpersonationStartRequest,
  request: Request,
  response: Response,
  context: AuthContext = Depends(get_auth_context),
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  check_rate_limit(key=f"admin:impersonation:start:{admin.id}", limit=20, window_seconds=60)
  request_id, user_agent, ip = request_meta(request)
  target_user, access_token, impersonation = start_impersonation(
    db,
    session=context.session,
    actor_user=admin,
    target_user_id=payload.target_user_id,
    reason=payload.reason,
    request_id=request_id,
    user_agent=user_agent,
    ip=ip,
  )
  db.commit()
  response.set_cookie(
    settings.access_cookie_name,
    access_token,
    httponly=True,
    secure=settings.cookie_secure,
    samesite="lax",
    max_age=settings.access_token_ttl_seconds,
    path="/",
  )
  return auth_me_response(db=db, session=context.session, effective_user=target_user, actor_user=admin, impersonation=impersonation)


@router.post("/impersonation/stop", response_model=ImpersonationAuthResponse)
def admin_stop_impersonation_endpoint(
  request: Request,
  response: Response,
  context: AuthContext = Depends(get_auth_context),
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  check_rate_limit(key=f"admin:impersonation:stop:{admin.id}", limit=30, window_seconds=60)
  access_token = stop_impersonation(db, session=context.session, actor_user=admin, request_id=getattr(request.state, "request_id", None))
  db.commit()
  response.set_cookie(
    settings.access_cookie_name,
    access_token,
    httponly=True,
    secure=settings.cookie_secure,
    samesite="lax",
    max_age=settings.access_token_ttl_seconds,
    path="/",
  )
  return auth_me_response(db=db, session=context.session, effective_user=admin, actor_user=admin, impersonation=None)


@router.get("/markets/review", response_model=AdminReviewList)
def admin_market_reviews_endpoint(
  limit: int = Query(default=50, ge=1, le=100),
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  _ = admin
  return {"items": [review_to_response(review) for review in list_reviews(db, limit=limit)], "next_cursor": None}


@router.get("/data-sources", response_model=DataSourceList)
def admin_data_sources_endpoint(
  category_slug: str | None = Query(default=None),
  limit: int = Query(default=100, ge=1, le=250),
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  _ = admin
  return {"items": [source_to_response(source) for source in list_sources(db, category_slug=category_slug, limit=limit)], "next_cursor": None}


@router.post("/data-sources", response_model=DataSourceResponse, status_code=201)
def admin_create_data_source_endpoint(
  payload: DataSourceCreate,
  request: Request,
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  check_rate_limit(key=f"admin:data-source:create:{admin.id}", limit=60, window_seconds=60)
  source = create_source(db, payload=payload, admin=admin, request_id=getattr(request.state, "request_id", None))
  db.commit()
  return source_to_response(source)


@router.post("/data-sources/{source_id}/test", response_model=DataSourceTestResponse)
def admin_test_data_source_endpoint(
  source_id: str,
  request: Request,
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  source = test_source(db, source_id=source_id, admin=admin, request_id=getattr(request.state, "request_id", None))
  db.commit()
  return {
    "source_id": source_to_response(source)["id"],
    "status": "complete",
    "health_status": source.health_status,
    "checked_at": source.last_checked_at,
    "message": "Local V1 source check completed. Provider fetchers can be attached without changing this contract.",
  }


@router.get("/source-events", response_model=SourceEventList)
def admin_source_events_endpoint(
  category_slug: str | None = Query(default=None),
  limit: int = Query(default=100, ge=1, le=250),
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  _ = admin
  return {"items": [event_to_response(event) for event in list_events(db, category_slug=category_slug, limit=limit)], "next_cursor": None}


@router.post("/ingestion-runs", response_model=IngestionRunResponse)
def admin_ingestion_run_endpoint(
  payload: IngestionRunCreate,
  request: Request,
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  check_rate_limit(key=f"admin:ingestion-run:{admin.id}", limit=30, window_seconds=60)
  events, skipped = run_ingestion(db, payload=payload, admin=admin, request_id=getattr(request.state, "request_id", None))
  db.commit()
  return {"status": "complete", "created_events": len(events), "skipped_duplicates": skipped, "items": [event_to_response(event) for event in events]}


@router.get("/market-drafts", response_model=MarketDraftList)
def admin_market_drafts_endpoint(
  status: str | None = Query(default=None),
  origin: str | None = Query(default=None),
  limit: int = Query(default=100, ge=1, le=250),
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  _ = admin
  return {"items": [draft_to_response(draft) for draft in list_drafts(db, status=status, origin=origin, limit=limit)], "next_cursor": None}


@router.post("/market-drafts", response_model=MarketDraftResponse, status_code=201)
async def admin_create_market_draft_endpoint(
  payload: MarketDraftCreate,
  request: Request,
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  check_rate_limit(key=f"admin:market-draft:create:{admin.id}", limit=60, window_seconds=60)
  draft = create_draft(db, payload=payload, admin=admin, request_id=getattr(request.state, "request_id", None))
  db.commit()
  await publish_pending_events(db)
  db.commit()
  return draft_to_response(draft)


@router.get("/market-drafts/{draft_id}", response_model=MarketDraftResponse)
def admin_market_draft_detail_endpoint(
  draft_id: str,
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  _ = admin
  return draft_to_response(get_draft_or_404(db, draft_id))


@router.patch("/market-drafts/{draft_id}", response_model=MarketDraftResponse)
def admin_update_market_draft_endpoint(
  draft_id: str,
  payload: MarketDraftPatch,
  request: Request,
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  draft = update_draft(db, draft_id=draft_id, payload=payload, admin=admin, request_id=getattr(request.state, "request_id", None))
  db.commit()
  return draft_to_response(draft)


@router.post("/market-drafts/{draft_id}/approve", response_model=MarketDraftActionResponse)
async def admin_approve_market_draft_endpoint(
  draft_id: str,
  request: Request,
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  draft = approve_draft(db, draft_id=draft_id, admin=admin, request_id=getattr(request.state, "request_id", None))
  db.commit()
  await publish_pending_events(db)
  db.commit()
  return {"status": draft.status, "draft_id": draft_to_response(draft)["id"], "market_id": draft.listed_market_id}


@router.post("/market-drafts/{draft_id}/reject", response_model=MarketDraftActionResponse)
async def admin_reject_market_draft_endpoint(
  draft_id: str,
  request: Request,
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  draft = reject_draft(db, draft_id=draft_id, admin=admin, request_id=getattr(request.state, "request_id", None))
  db.commit()
  await publish_pending_events(db)
  db.commit()
  return {"status": draft.status, "draft_id": draft_to_response(draft)["id"], "market_id": draft.listed_market_id}


@router.post("/market-drafts/{draft_id}/list", response_model=MarketDraftActionResponse)
async def admin_list_market_draft_endpoint(
  draft_id: str,
  request: Request,
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  draft = list_draft(db, draft_id=draft_id, admin=admin, request_id=getattr(request.state, "request_id", None))
  db.commit()
  await publish_pending_events(db)
  db.commit()
  return {"status": draft.status, "draft_id": draft_to_response(draft)["id"], "market_id": draft.listed_market_id}


@router.post("/ai-market-generation/run", response_model=AIMarketGenerationRunResponse)
async def admin_ai_market_generation_endpoint(
  payload: AIMarketGenerationRunRequest,
  request: Request,
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  check_rate_limit(key=f"admin:ai-market-generation:{admin.id}", limit=20, window_seconds=60)
  drafts = generate_ai_drafts(db, payload=payload, admin=admin, request_id=getattr(request.state, "request_id", None))
  db.commit()
  await publish_pending_events(db)
  db.commit()
  return {"status": "complete", "created_drafts": len(drafts), "items": [draft_to_response(draft) for draft in drafts]}


@router.get("/markets/review/{review_id}", response_model=AdminReviewResponse)
def admin_market_review_detail_endpoint(
  review_id: str,
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  _ = admin
  return review_to_response(get_review_or_404(db, review_id=review_id))


@router.post("/markets/{market_id}/approve", response_model=AdminActionResponse)
async def admin_approve_market_endpoint(
  market_id: str,
  request: Request,
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  check_rate_limit(key=f"admin:market:approve:{admin.id}", limit=120, window_seconds=60)
  market = set_market_status(db, market_id=market_id, status="OPEN", admin=admin, request_id=getattr(request.state, "request_id", None))
  db.commit()
  await publish_pending_events(db)
  db.commit()
  return {"status": market.status, "market_id": market.id}


@router.post("/markets/{market_id}/pause", response_model=AdminActionResponse)
async def admin_pause_market_endpoint(
  market_id: str,
  request: Request,
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  check_rate_limit(key=f"admin:market:pause:{admin.id}", limit=120, window_seconds=60)
  market = set_market_status(db, market_id=market_id, status="PAUSED", admin=admin, request_id=getattr(request.state, "request_id", None))
  db.commit()
  await publish_pending_events(db)
  db.commit()
  return {"status": market.status, "market_id": market.id}


@router.post("/markets/{market_id}/close", response_model=AdminActionResponse)
async def admin_close_market_endpoint(
  market_id: str,
  request: Request,
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  check_rate_limit(key=f"admin:market:close:{admin.id}", limit=120, window_seconds=60)
  market = close_market(db, market_id=market_id, admin=admin, request_id=getattr(request.state, "request_id", None))
  db.commit()
  await publish_pending_events(db)
  db.commit()
  return {"status": market.status, "market_id": market.id}


@router.post("/markets/{market_id}/evidence", response_model=EvidenceResponse, status_code=201)
async def admin_add_evidence_endpoint(
  market_id: str,
  payload: EvidenceCreate,
  request: Request,
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  evidence = add_evidence(
    db,
    market_id=market_id,
    source_name=payload.source_name,
    source_url=payload.source_url,
    captured_payload=payload.captured_payload,
    admin=admin,
    request_id=getattr(request.state, "request_id", None),
  )
  db.commit()
  await publish_pending_events(db)
  db.commit()
  return evidence_to_response(evidence)


@router.post("/markets/{market_id}/resolution-proposals", response_model=ResolutionProposalResponse, status_code=201)
async def admin_create_resolution_proposal_endpoint(
  market_id: str,
  payload: ResolutionProposalCreate,
  request: Request,
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  proposal = create_resolution_proposal(
    db,
    market_id=market_id,
    result=payload.result,
    winning_outcome_id=payload.winning_outcome_id,
    reason=payload.reason,
    maker=admin,
    request_id=getattr(request.state, "request_id", None),
  )
  db.commit()
  await publish_pending_events(db)
  db.commit()
  return proposal_to_response(proposal)


@router.post("/resolution-proposals/{proposal_id}/approve", response_model=ResolutionProposalResponse)
async def admin_approve_resolution_proposal_endpoint(
  proposal_id: str,
  request: Request,
  checker: User = Depends(require_checker),
  db: Session = Depends(get_db),
):
  proposal = approve_resolution_proposal(db, proposal_id=proposal_id, checker=checker, request_id=getattr(request.state, "request_id", None))
  db.commit()
  await publish_pending_events(db)
  db.commit()
  return proposal_to_response(proposal)


@router.post("/markets/{market_id}/settle", response_model=SettlementResponse)
async def admin_settle_market_endpoint(
  market_id: str,
  request: Request,
  idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
  admin: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  settlement = settle_market(
    db,
    market_id=market_id,
    admin=admin,
    idempotency_key=idempotency_key,
    request_id=getattr(request.state, "request_id", None),
  )
  db.commit()
  await publish_pending_events(db)
  db.commit()
  return settlement_to_response(settlement)


@router.post("/analytics/recompute", response_model=RecomputeResponse)
def admin_recompute_analytics_endpoint(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
  _ = admin
  counts = recompute_all(db)
  db.commit()
  return {"status": "complete", **counts}
