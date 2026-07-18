from hashlib import sha256


def public_id(prefix: str, internal_id: str | None) -> str | None:
  if not internal_id:
    return None
  digest = sha256(internal_id.encode("utf-8")).hexdigest()[:10].upper()
  return f"{prefix}-{digest}"


def matches_public_id(prefix: str, internal_id: str, candidate: str) -> bool:
  return candidate == internal_id or candidate == public_id(prefix, internal_id)
