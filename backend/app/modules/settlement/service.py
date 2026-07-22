from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import AppError
from app.core.public_ids import matches_public_id, public_id
from app.core.security import utc_now
from app.modules.audit.service import write_audit_log
from app.modules.markets.models import Market, OracleEvidence, Outcome
from app.modules.orders.service import cancel_market_open_orders
from app.modules.positions.models import Position
from app.modules.realtime.service import write_admin_event, write_market_event, write_user_event
from app.modules.settlement.models import ResolutionProposal, Settlement, SettlementItem
from app.modules.users.models import User
from app.modules.wallets.service import credit_available_cash


def evidence_to_response(evidence: OracleEvidence) -> dict:
  return {
    "id": public_id("EVD", evidence.id),
    "market_id": evidence.market_id,
    "source_name": evidence.source_name,
    "source_url": evidence.source_url,
    "captured_payload": evidence.captured_payload_json,
    "captured_at": evidence.captured_at,
  }


def proposal_to_response(proposal: ResolutionProposal) -> dict:
  return {
    "id": public_id("RSP", proposal.id),
    "market_id": proposal.market_id,
    "winning_outcome_id": public_id("OUT", proposal.winning_outcome_id),
    "result": proposal.result,
    "reason": proposal.reason,
    "maker_user_id": public_id("USR", proposal.maker_user_id),
    "checker_user_id": public_id("USR", proposal.checker_user_id),
    "status": proposal.status,
    "created_at": proposal.created_at,
    "approved_at": proposal.approved_at,
  }


def settlement_to_response(settlement: Settlement) -> dict:
  return {
    "id": public_id("SET", settlement.id),
    "market_id": settlement.market_id,
    "resolution_proposal_id": public_id("RSP", settlement.resolution_proposal_id),
    "status": settlement.status,
    "completed_at": settlement.completed_at,
    "items": [
      {
        "id": public_id("STI", item.id),
        "user_id": public_id("USR", item.user_id),
        "position_id": public_id("POS", item.position_id),
        "payout_minor": item.payout_minor,
        "created_at": item.created_at,
      }
      for item in settlement.items
    ],
  }


def close_market(db: Session, *, market_id: str, admin: User, request_id: str | None) -> Market:
  market = db.get(Market, market_id)
  if not market:
    raise AppError(404, "MARKET_NOT_FOUND", "Market was not found.")
  if market.status in {"RESOLVED", "VOIDED"}:
    return market
  if market.status not in {"OPEN", "PAUSED", "CLOSED", "PENDING_RESOLUTION"}:
    raise AppError(422, "MARKET_CANNOT_CLOSE", "Market cannot be closed from its current status.")
  cancelled = cancel_market_open_orders(db, market_id=market.id)
  market.status = "CLOSED"
  market.updated_at = utc_now()
  write_audit_log(
    db,
    event_type="MARKET_CLOSED",
    actor_user_id=admin.id,
    request_id=request_id,
    metadata={"market_id": market.id, "cancelled_orders": len(cancelled)},
  )
  write_market_event(db, event_type="market.status_changed", market_id=market.id, suffix="status", payload={"market_id": market.id, "status": market.status})
  return market


def add_evidence(
  db: Session,
  *,
  market_id: str,
  source_name: str,
  source_url: str | None,
  captured_payload: dict,
  admin: User,
  request_id: str | None,
) -> OracleEvidence:
  market = db.get(Market, market_id)
  if not market:
    raise AppError(404, "MARKET_NOT_FOUND", "Market was not found.")
  evidence = OracleEvidence(
    market_id=market.id,
    source_name=source_name,
    source_url=source_url,
    captured_payload_json=captured_payload,
  )
  db.add(evidence)
  db.flush()
  write_audit_log(
    db,
    event_type="ORACLE_EVIDENCE_ADDED",
    actor_user_id=admin.id,
    request_id=request_id,
    metadata={"market_id": market.id, "evidence_id": evidence.id},
  )
  return evidence


def create_resolution_proposal(
  db: Session,
  *,
  market_id: str,
  result: str,
  winning_outcome_id: str | None,
  reason: str,
  maker: User,
  request_id: str | None,
) -> ResolutionProposal:
  market = db.get(Market, market_id)
  if not market:
    raise AppError(404, "MARKET_NOT_FOUND", "Market was not found.")
  if market.status not in {"CLOSED", "PENDING_RESOLUTION"}:
    raise AppError(422, "MARKET_NOT_CLOSED", "Market must be closed before resolution proposal.")
  if result == "RESOLVE":
    if not winning_outcome_id:
      raise AppError(422, "WINNING_OUTCOME_REQUIRED", "Winning outcome is required for resolved markets.")
    outcome = db.get(Outcome, winning_outcome_id)
    if not outcome:
      for candidate in db.scalars(select(Outcome).where(Outcome.market_id == market.id)).all():
        if matches_public_id("OUT", candidate.id, winning_outcome_id):
          outcome = candidate
          break
    if not outcome or outcome.market_id != market.id:
      raise AppError(422, "INVALID_WINNING_OUTCOME", "Winning outcome does not belong to this market.")
    winning_outcome_id = outcome.id
  elif winning_outcome_id:
    raise AppError(422, "VOID_CANNOT_HAVE_WINNER", "Void proposals cannot include a winning outcome.")

  existing_pending = db.scalar(
    select(ResolutionProposal).where(
      ResolutionProposal.market_id == market.id,
      ResolutionProposal.status == "PENDING",
    )
  )
  if existing_pending:
    raise AppError(409, "PENDING_PROPOSAL_EXISTS", "A pending resolution proposal already exists for this market.")

  market.status = "PENDING_RESOLUTION"
  proposal = ResolutionProposal(
    market_id=market.id,
    winning_outcome_id=winning_outcome_id,
    result=result,
    reason=reason,
    maker_user_id=maker.id,
    status="PENDING",
  )
  db.add(proposal)
  db.flush()
  write_audit_log(
    db,
    event_type="RESOLUTION_PROPOSED",
    actor_user_id=maker.id,
    request_id=request_id,
    metadata={"market_id": market.id, "proposal_id": proposal.id, "result": result},
  )
  return proposal


def approve_resolution_proposal(db: Session, *, proposal_id: str, checker: User, request_id: str | None) -> ResolutionProposal:
  proposal = db.get(ResolutionProposal, proposal_id)
  if not proposal:
    for candidate in db.scalars(select(ResolutionProposal)).all():
      if matches_public_id("RSP", candidate.id, proposal_id):
        proposal = candidate
        break
  if not proposal:
    raise AppError(404, "PROPOSAL_NOT_FOUND", "Resolution proposal was not found.")
  if proposal.status != "PENDING":
    return proposal
  if proposal.maker_user_id == checker.id:
    raise AppError(403, "MAKER_CHECKER_REQUIRED", "Resolution approval requires a different checker.")
  proposal.status = "APPROVED"
  proposal.checker_user_id = checker.id
  proposal.approved_at = utc_now()
  write_audit_log(
    db,
    event_type="RESOLUTION_APPROVED",
    actor_user_id=checker.id,
    request_id=request_id,
    metadata={"market_id": proposal.market_id, "proposal_id": proposal.id},
  )
  write_admin_event(db, event_type="admin.settlement_status.updated", suffix="settlement_status", market_id=proposal.market_id, payload={"market_id": proposal.market_id, "proposal_id": proposal.id, "status": proposal.status})
  return proposal


def settle_market(db: Session, *, market_id: str, admin: User, idempotency_key: str | None, request_id: str | None) -> Settlement:
  market = db.get(Market, market_id)
  if not market:
    raise AppError(404, "MARKET_NOT_FOUND", "Market was not found.")
  existing = db.scalar(select(Settlement).where(Settlement.market_id == market.id).options(selectinload(Settlement.items)))
  if existing:
    return existing

  proposal = db.scalar(
    select(ResolutionProposal)
    .where(ResolutionProposal.market_id == market.id, ResolutionProposal.status == "APPROVED")
    .order_by(ResolutionProposal.approved_at.desc())
  )
  if not proposal:
    raise AppError(422, "APPROVED_PROPOSAL_REQUIRED", "An approved resolution proposal is required before settlement.")

  settlement = Settlement(
    market_id=market.id,
    resolution_proposal_id=proposal.id,
    status="PROCESSING",
    idempotency_key=idempotency_key,
  )
  db.add(settlement)
  db.flush()

  positions = list(
    db.scalars(
      select(Position)
      .where(Position.market_id == market.id, Position.quantity > 0)
      .options(selectinload(Position.outcome))
      .order_by(Position.created_at.asc())
    ).all()
  )
  for position in positions:
    if proposal.result == "VOID":
      payout_minor = position.quantity * position.average_entry_price_minor
    elif position.outcome_id == proposal.winning_outcome_id:
      payout_minor = position.quantity * 100
    else:
      payout_minor = 0

    item = SettlementItem(
      settlement_id=settlement.id,
      user_id=position.user_id,
      position_id=position.id,
      payout_minor=payout_minor,
    )
    db.add(item)
    if payout_minor > 0:
      credit_available_cash(
        db,
        user_id=position.user_id,
        market_id=market.id,
        amount_minor=payout_minor,
        reference_id=f"{settlement.id}:{position.id}",
        transaction_type="VOID_REFUND" if proposal.result == "VOID" else "SETTLEMENT_CREDIT",
      )
      write_user_event(
        db,
        event_type="wallet.updated",
        user_id=position.user_id,
        suffix="wallet",
        market_id=market.id,
        payload={"market_id": market.id, "payout_minor": payout_minor, "reason": proposal.result},
      )
    write_user_event(
      db,
      event_type="position.updated",
      user_id=position.user_id,
      suffix="positions",
      market_id=market.id,
      payload={"market_id": market.id, "position_id": position.id, "status": "SETTLED"},
    )
    position.realized_pnl_minor += payout_minor - (position.quantity * position.average_entry_price_minor)
    position.quantity = 0
    position.locked_quantity = 0
    position.average_entry_price_minor = 0
    position.status = "SETTLED"

  settlement.status = "COMPLETE"
  settlement.completed_at = utc_now()
  market.status = "VOIDED" if proposal.result == "VOID" else "RESOLVED"
  market.updated_at = utc_now()
  write_audit_log(
    db,
    event_type="MARKET_SETTLED",
    actor_user_id=admin.id,
    request_id=request_id,
    metadata={"market_id": market.id, "settlement_id": settlement.id, "items": len(positions)},
  )
  write_market_event(db, event_type="market.status_changed", market_id=market.id, suffix="status", payload={"market_id": market.id, "status": market.status})
  write_admin_event(db, event_type="admin.settlement_status.updated", suffix="settlement_status", market_id=market.id, payload={"market_id": market.id, "settlement_id": settlement.id, "status": settlement.status})
  db.flush()
  db.refresh(settlement, attribute_names=["items"])
  return settlement
