from typing import Any

from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.public_ids import public_id
from app.core.security import utc_now
from app.modules.realtime.manager import manager
from app.modules.realtime.broker import broker
from app.modules.realtime.models import RealtimeEvent


def next_sequence(db: Session) -> int:
  current = db.scalar(select(func.max(RealtimeEvent.sequence))) or 0
  return int(current) + 1


def event_envelope(event: RealtimeEvent) -> dict[str, Any]:
  return {
    "event_id": public_id("EVT", event.id),
    "event_type": event.event_type,
    "sequence": event.sequence,
    "market_id": event.market_id,
    "created_at": event.created_at.isoformat() if event.created_at else None,
    "payload": public_payload(event.payload_json),
  }


def public_payload(value: Any, key: str | None = None) -> Any:
  if isinstance(value, dict):
    return {item_key: public_payload(item_value, item_key) for item_key, item_value in value.items()}
  if isinstance(value, list):
    return [public_payload(item, key) for item in value]
  if not isinstance(value, str) or key is None:
    return value
  prefixes = {
    "event_id": "EVT",
    "order_id": "ORD",
    "outcome_id": "OUT",
    "trade_id": "TRD",
    "position_id": "POS",
    "proposal_id": "RSP",
    "resolution_proposal_id": "RSP",
    "settlement_id": "SET",
    "user_id": "USR",
    "actor_user_id": "USR",
    "target_user_id": "USR",
    "impersonation_session_id": "SES",
    "evidence_id": "EVD",
    "suggestion_id": "SUG",
  }
  prefix = prefixes.get(key)
  return public_id(prefix, value) if prefix else value


def json_safe(value: Any) -> Any:
  if isinstance(value, datetime | date):
    return value.isoformat()
  if isinstance(value, dict):
    return {key: json_safe(item) for key, item in value.items()}
  if isinstance(value, list):
    return [json_safe(item) for item in value]
  return value


def write_event(
  db: Session,
  *,
  event_type: str,
  channel: str,
  payload: dict[str, Any],
  scope_type: str = "PUBLIC",
  scope_id: str | None = None,
  market_id: str | None = None,
  user_id: str | None = None,
) -> RealtimeEvent:
  event = RealtimeEvent(
    sequence=next_sequence(db),
    event_type=event_type,
    channel=channel,
    scope_type=scope_type,
    scope_id=scope_id,
    market_id=market_id,
    user_id=user_id,
    payload_json=json_safe(payload),
    publish_status="PENDING",
  )
  db.add(event)
  db.flush()
  return event


async def publish_pending_events(db: Session) -> None:
  events = list(
    db.scalars(
      select(RealtimeEvent)
      .where(RealtimeEvent.publish_status == "PENDING")
      .order_by(RealtimeEvent.sequence.asc())
      .limit(100)
    ).all()
  )
  for event in events:
    await publish_event(event)


async def publish_event(event: RealtimeEvent) -> None:
  envelope = event_envelope(event)
  await manager.publish(event.channel, envelope)
  await broker.publish(event.channel, envelope)
  event.publish_status = "PUBLISHED"
  event.published_at = utc_now()


def write_market_event(db: Session, *, event_type: str, market_id: str, payload: dict[str, Any], suffix: str) -> RealtimeEvent:
  return write_event(
    db,
    event_type=event_type,
    channel=f"market.{suffix}.{market_id}",
    scope_type="MARKET",
    scope_id=market_id,
    market_id=market_id,
    payload=payload,
  )


def write_user_event(db: Session, *, event_type: str, user_id: str, payload: dict[str, Any], suffix: str, market_id: str | None = None) -> RealtimeEvent:
  return write_event(
    db,
    event_type=event_type,
    channel=f"user.{suffix}.{user_id}",
    scope_type="USER",
    scope_id=user_id,
    user_id=user_id,
    market_id=market_id,
    payload=payload,
  )


def write_admin_event(db: Session, *, event_type: str, payload: dict[str, Any], suffix: str, market_id: str | None = None) -> RealtimeEvent:
  return write_event(
    db,
    event_type=event_type,
    channel=f"admin.{suffix}",
    scope_type="ADMIN",
    scope_id=None,
    market_id=market_id,
    payload=payload,
  )
