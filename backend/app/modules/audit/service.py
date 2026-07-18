from typing import Any

from sqlalchemy.orm import Session

from app.modules.audit.models import AuditLog


def write_audit_log(
  db: Session,
  *,
  event_type: str,
  actor_user_id: str | None = None,
  target_user_id: str | None = None,
  request_id: str | None = None,
  ip_hash: str | None = None,
  user_agent: str | None = None,
  metadata: dict[str, Any] | None = None,
) -> AuditLog:
  log = AuditLog(
    event_type=event_type,
    actor_user_id=actor_user_id,
    target_user_id=target_user_id,
    request_id=request_id,
    ip_hash=ip_hash,
    user_agent=user_agent,
    metadata_json=metadata or {},
  )
  db.add(log)
  return log
