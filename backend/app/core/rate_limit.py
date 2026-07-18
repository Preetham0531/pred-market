from app.core.errors import AppError
from app.core.security import utc_now
from app.db.redis import get_redis

_memory_counts: dict[str, tuple[int, float]] = {}


def check_rate_limit(*, key: str, limit: int, window_seconds: int) -> None:
  redis_key = f"rate:{key}"
  try:
    redis = get_redis()
    count = redis.incr(redis_key)
    if count == 1:
      redis.expire(redis_key, window_seconds)
  except Exception:
    now = utc_now().timestamp()
    current_count, expires_at = _memory_counts.get(redis_key, (0, 0))
    if expires_at <= now:
      current_count = 0
      expires_at = now + window_seconds
    count = current_count + 1
    _memory_counts[redis_key] = (count, expires_at)

  if count > limit:
    raise AppError(
      429,
      "RATE_LIMITED",
      "Too many requests. Wait briefly and try again.",
      {"limit": limit, "window_seconds": window_seconds},
    )
