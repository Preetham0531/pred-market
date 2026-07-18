from app.core.security import new_token
from app.db.redis import get_redis

WS_TICKET_PREFIX = "ws_ticket:"
_LOCAL_TICKETS: dict[str, dict[str, object]] = {}


def create_ws_ticket(user_id: str, roles: list[str], ttl_seconds: int = 60) -> str:
  ticket = f"ws_{new_token(24)}"
  try:
    redis = get_redis()
    redis.hset(f"{WS_TICKET_PREFIX}{ticket}", mapping={"user_id": user_id, "roles": ",".join(roles)})
    redis.expire(f"{WS_TICKET_PREFIX}{ticket}", ttl_seconds)
  except Exception:
    _LOCAL_TICKETS[ticket] = {"user_id": user_id, "roles": roles}
  return ticket


def consume_ws_ticket(ticket: str | None) -> dict[str, object] | None:
  if not ticket:
    return None
  try:
    redis = get_redis()
    key = f"{WS_TICKET_PREFIX}{ticket}"
    payload = redis.hgetall(key)
    if not payload:
      return None
    redis.delete(key)
    return {"user_id": payload.get("user_id"), "roles": [role for role in payload.get("roles", "").split(",") if role]}
  except Exception:
    return _LOCAL_TICKETS.pop(ticket, None)
