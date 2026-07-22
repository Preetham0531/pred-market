from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password, utc_now, validate_password_strength
from app.db.session import SessionLocal
from app.modules.audit.service import write_audit_log
from app.modules.users.models import User, UserRole
from app.modules.wallets.service import get_or_create_wallet


def bootstrap_admin_in_session(db, *, email: str, password: str) -> str:
  user = db.scalar(select(User).where(User.email == email))
  created = user is None
  if created:
    if not password:
      raise RuntimeError("ADMIN_BOOTSTRAP_PASSWORD is required when creating the first admin.")
    validate_password_strength(password)
    user = User(
      email=email,
      display_name="Pred-Market Admin",
      password_hash=hash_password(password),
      email_verified_at=utc_now(),
    )
    db.add(user)
    db.flush()

  assert user is not None
  existing_roles = {role.role for role in user.roles}
  for role in ("USER", "ADMIN"):
    if role not in existing_roles:
      user.roles.append(UserRole(role=role, created_at=utc_now()))
  if user.email_verified_at is None:
    user.email_verified_at = utc_now()
  get_or_create_wallet(db, user.id)
  write_audit_log(
    db,
    event_type="ADMIN_BOOTSTRAPPED" if created else "ADMIN_BOOTSTRAP_CONFIRMED",
    actor_user_id=user.id,
    target_user_id=user.id,
    metadata={"email": email, "created": created},
  )
  return "created" if created else "already-present"


def bootstrap_admin() -> str:
  email = settings.admin_bootstrap_email.strip().lower()
  if not email:
    raise RuntimeError("ADMIN_BOOTSTRAP_EMAIL is required.")

  with SessionLocal() as db:
    result = bootstrap_admin_in_session(db, email=email, password=settings.admin_bootstrap_password)
    db.commit()
  return result


def main() -> None:
  result = bootstrap_admin()
  print(f"Admin bootstrap complete: {result}.")


if __name__ == "__main__":
  main()
