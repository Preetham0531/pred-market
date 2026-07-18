from datetime import timedelta

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.core.public_ids import matches_public_id, public_id
from app.core.security import as_utc, create_jwt, expires_in, hash_optional, hash_password, hash_token, new_token, utc_now, verify_password
from app.modules.audit.service import write_audit_log
from app.modules.auth.models import AdminImpersonationSession, AuthSession, EmailVerificationToken, PasswordResetToken
from app.modules.users.models import User, UserRole
from app.modules.wallets.service import get_or_create_wallet

GENERIC_CREDENTIAL_ERROR = "Invalid email or password."


def normalize_email(email: str) -> str:
  return email.strip().lower()


def roles_for_user(user: User) -> list[str]:
  roles = {role.role for role in user.roles}
  if "ADMIN" in roles:
    return ["USER", "ADMIN"]
  return ["USER"]


def user_to_response(user: User) -> dict:
  return {
    "id": public_id("USR", user.id),
    "email": user.email,
    "display_name": user.display_name,
    "status": user.status,
    "roles": roles_for_user(user),
    "email_verified_at": user.email_verified_at,
    "kyc_status": user.kyc_status,
    "jurisdiction_code": user.jurisdiction_code,
  }


def auth_me_response(
  *,
  effective_user: User,
  actor_user: User,
  impersonation: AdminImpersonationSession | None = None,
) -> dict:
  return {
    "user": user_to_response(effective_user),
    "actor": user_to_response(actor_user),
    "impersonation": impersonation_to_response(impersonation) if impersonation else None,
  }


def impersonation_to_response(impersonation: AdminImpersonationSession) -> dict:
  return {
    "active": True,
    "session_id": public_id("SES", impersonation.id),
    "mode": impersonation.mode,
    "actor_user_id": public_id("USR", impersonation.actor_user_id),
    "target_user_id": public_id("USR", impersonation.target_user_id),
    "started_at": impersonation.started_at,
  }


def get_user_by_email(db: Session, email: str) -> User | None:
  return db.scalar(select(User).where(User.email == normalize_email(email)))


def get_user_by_public_or_internal_id(db: Session, user_id: str) -> User | None:
  user = db.get(User, user_id)
  if user:
    return user
  for candidate in db.scalars(select(User)).all():
    if matches_public_id("USR", candidate.id, user_id):
      return candidate
  return None


def create_session(
  db: Session,
  user: User,
  *,
  request_id: str | None,
  user_agent: str | None,
  ip: str | None,
) -> tuple[str, str, AuthSession]:
  refresh_token = new_token()
  csrf_token = new_token(24)
  session = AuthSession(
    user_id=user.id,
    refresh_token_hash=hash_token(refresh_token),
    csrf_token_hash=hash_token(csrf_token),
    user_agent=user_agent,
    ip_hash=hash_optional(ip),
    expires_at=expires_in(settings.session_ttl_seconds),
  )
  db.add(session)
  db.flush()
  write_audit_log(
    db,
    event_type="SESSION_CREATED",
    actor_user_id=user.id,
    target_user_id=user.id,
    request_id=request_id,
    ip_hash=hash_optional(ip),
    user_agent=user_agent,
  )
  return refresh_token, csrf_token, session


def get_active_impersonation(db: Session, session_id: str) -> AdminImpersonationSession | None:
  return db.scalar(
    select(AdminImpersonationSession).where(
      AdminImpersonationSession.auth_session_id == session_id,
      AdminImpersonationSession.ended_at.is_(None),
    )
  )


def create_access_token_for_session(db: Session, session: AuthSession) -> str:
  actor_user = session.user
  effective_user = actor_user
  impersonation = get_active_impersonation(db, session.id)
  payload = {
    "sub": actor_user.id,
    "sid": session.id,
    "roles": roles_for_user(actor_user),
  }
  if impersonation:
    effective_user = impersonation.target_user
    payload.update(
      {
        "sub": effective_user.id,
        "roles": roles_for_user(effective_user),
        "actor_sub": actor_user.id,
        "impersonation_session_id": impersonation.id,
        "mode": impersonation.mode,
      }
    )
  return create_jwt(payload, ttl_seconds=settings.access_token_ttl_seconds)


def sign_up(
  db: Session,
  *,
  email: str,
  password: str,
  display_name: str | None,
  jurisdiction_hint: str | None,
  request_id: str | None,
  user_agent: str | None,
  ip: str | None,
) -> tuple[User, str, str, str]:
  normalized_email = normalize_email(email)
  if get_user_by_email(db, normalized_email):
    raise AppError(409, "EMAIL_ALREADY_EXISTS", "An account with this email already exists.")

  user = User(
    email=normalized_email,
    password_hash=hash_password(password),
    display_name=display_name,
    jurisdiction_code=jurisdiction_hint,
  )
  user.roles.append(UserRole(role="USER", created_at=utc_now()))
  db.add(user)
  db.flush()
  get_or_create_wallet(db, user.id)

  verification_token = new_token()
  db.add(
    EmailVerificationToken(
      user_id=user.id,
      token_hash=hash_token(verification_token),
      expires_at=utc_now() + timedelta(hours=24),
    )
  )
  write_audit_log(
    db,
    event_type="USER_SIGNED_UP",
    actor_user_id=user.id,
    target_user_id=user.id,
    request_id=request_id,
    ip_hash=hash_optional(ip),
    user_agent=user_agent,
    metadata={"email_verification_token_dev": verification_token},
  )
  refresh_token, csrf_token, session = create_session(db, user, request_id=request_id, user_agent=user_agent, ip=ip)
  access_token = create_access_token_for_session(db, session)
  return user, access_token, refresh_token, csrf_token


def sign_in(
  db: Session,
  *,
  email: str,
  password: str,
  request_id: str | None,
  user_agent: str | None,
  ip: str | None,
) -> tuple[User, str, str, str]:
  user = get_user_by_email(db, email)
  if not user:
    raise AppError(401, "INVALID_CREDENTIALS", GENERIC_CREDENTIAL_ERROR)

  if user.status in {"SUSPENDED", "CLOSED"}:
    raise AppError(403, "ACCOUNT_UNAVAILABLE", "This account cannot sign in.")

  now = utc_now()
  if user.locked_until and as_utc(user.locked_until) > now:
    raise AppError(423, "ACCOUNT_LOCKED", "This account is temporarily locked.")

  if not verify_password(password, user.password_hash):
    user.failed_login_count += 1
    if user.failed_login_count >= settings.account_lock_threshold:
      user.locked_until = now + timedelta(minutes=settings.account_lock_minutes)
      write_audit_log(
        db,
        event_type="ACCOUNT_LOCKED",
        actor_user_id=user.id,
        target_user_id=user.id,
        request_id=request_id,
        ip_hash=hash_optional(ip),
        user_agent=user_agent,
      )
    raise AppError(401, "INVALID_CREDENTIALS", GENERIC_CREDENTIAL_ERROR)

  user.failed_login_count = 0
  user.locked_until = None
  user.last_login_at = now
  refresh_token, csrf_token, session = create_session(db, user, request_id=request_id, user_agent=user_agent, ip=ip)
  access_token = create_access_token_for_session(db, session)
  write_audit_log(
    db,
    event_type="USER_SIGNED_IN",
    actor_user_id=user.id,
    target_user_id=user.id,
    request_id=request_id,
    ip_hash=hash_optional(ip),
    user_agent=user_agent,
  )
  return user, access_token, refresh_token, csrf_token


def get_session_by_token(db: Session, refresh_token: str | None) -> AuthSession | None:
  if not refresh_token:
    return None
  session = db.scalar(select(AuthSession).where(AuthSession.refresh_token_hash == hash_token(refresh_token)))
  if not session or session.revoked_at or as_utc(session.expires_at) <= utc_now():
    return None
  session.last_seen_at = utc_now()
  return session


def revoke_session(db: Session, session: AuthSession, *, reason: str, request_id: str | None = None) -> None:
  session.revoked_at = utc_now()
  session.revoked_reason = reason
  write_audit_log(
    db,
    event_type="SESSION_REVOKED",
    actor_user_id=session.user_id,
    target_user_id=session.user_id,
    request_id=request_id,
    metadata={"reason": reason},
  )


def refresh_session(db: Session, session: AuthSession, *, request_id: str | None) -> tuple[User, str, str, str]:
  user = session.user
  active_impersonation = get_active_impersonation(db, session.id)
  revoke_session(db, session, reason="ROTATED", request_id=request_id)
  refresh_token, csrf_token, new_session = create_session(db, user, request_id=request_id, user_agent=session.user_agent, ip=None)
  if active_impersonation:
    active_impersonation.auth_session_id = new_session.id
  access_token = create_access_token_for_session(db, new_session)
  write_audit_log(db, event_type="SESSION_REFRESHED", actor_user_id=user.id, target_user_id=user.id, request_id=request_id)
  return user, access_token, refresh_token, csrf_token


def get_session_by_id(db: Session, session_id: str | None) -> AuthSession | None:
  if not session_id:
    return None
  session = db.get(AuthSession, session_id)
  if not session or session.revoked_at or as_utc(session.expires_at) <= utc_now():
    return None
  session.last_seen_at = utc_now()
  return session


def list_admin_switchable_users(db: Session, *, query: str | None, limit: int) -> list[User]:
  statement = select(User).where(User.status == "ACTIVE").order_by(User.email.asc()).limit(limit)
  if query:
    pattern = f"%{query.strip().lower()}%"
    statement = statement.where(or_(User.email.ilike(pattern), User.display_name.ilike(pattern)))
  return list(db.scalars(statement).all())


def start_impersonation(
  db: Session,
  *,
  session: AuthSession,
  actor_user: User,
  target_user_id: str,
  reason: str,
  request_id: str | None,
  user_agent: str | None,
  ip: str | None,
) -> tuple[User, str, AdminImpersonationSession]:
  actor_roles = set(roles_for_user(actor_user))
  if "ADMIN" not in actor_roles:
    raise AppError(403, "FORBIDDEN", "Only admins can switch user view.")
  target_user = get_user_by_public_or_internal_id(db, target_user_id)
  if not target_user or target_user.status != "ACTIVE":
    raise AppError(404, "USER_NOT_FOUND", "Switch target user was not found.")
  if "ADMIN" in set(roles_for_user(target_user)):
    write_audit_log(
      db,
      event_type="ADMIN_IMPERSONATION_DENIED",
      actor_user_id=actor_user.id,
      target_user_id=target_user.id,
      request_id=request_id,
      ip_hash=hash_optional(ip),
      user_agent=user_agent,
      metadata={"reason": "TARGET_IS_ADMIN"},
    )
    db.flush()
    raise AppError(403, "ADMIN_IMPERSONATION_FORBIDDEN", "Admins cannot switch into another admin profile.")
  existing = get_active_impersonation(db, session.id)
  if existing:
    existing.ended_at = utc_now()
    existing.ended_reason = "REPLACED"
  impersonation = AdminImpersonationSession(
    auth_session_id=session.id,
    actor_user_id=actor_user.id,
    target_user_id=target_user.id,
    mode="READ_ONLY",
    reason=reason.strip() or "Admin support review",
    ip_hash=hash_optional(ip),
    user_agent=user_agent,
  )
  db.add(impersonation)
  db.flush()
  write_audit_log(
    db,
    event_type="ADMIN_IMPERSONATION_STARTED",
    actor_user_id=actor_user.id,
    target_user_id=target_user.id,
    request_id=request_id,
    ip_hash=hash_optional(ip),
    user_agent=user_agent,
    metadata={"impersonation_session_id": impersonation.id, "mode": impersonation.mode, "reason": impersonation.reason},
  )
  return target_user, create_access_token_for_session(db, session), impersonation


def stop_impersonation(
  db: Session,
  *,
  session: AuthSession,
  actor_user: User,
  request_id: str | None,
  reason: str = "ADMIN_RETURNED",
) -> str:
  impersonation = get_active_impersonation(db, session.id)
  if impersonation:
    impersonation.ended_at = utc_now()
    impersonation.ended_reason = reason
    write_audit_log(
      db,
      event_type="ADMIN_IMPERSONATION_STOPPED",
      actor_user_id=actor_user.id,
      target_user_id=impersonation.target_user_id,
      request_id=request_id,
      metadata={"impersonation_session_id": impersonation.id, "reason": reason},
    )
  return create_access_token_for_session(db, session)


def request_email_verification(db: Session, user: User, *, request_id: str | None) -> str:
  token = new_token()
  db.add(EmailVerificationToken(user_id=user.id, token_hash=hash_token(token), expires_at=utc_now() + timedelta(hours=24)))
  write_audit_log(
    db,
    event_type="EMAIL_VERIFICATION_REQUESTED",
    actor_user_id=user.id,
    target_user_id=user.id,
    request_id=request_id,
    metadata={"email_verification_token_dev": token},
  )
  return token


def confirm_email_verification(db: Session, token: str, *, request_id: str | None) -> User:
  token_row = db.scalar(select(EmailVerificationToken).where(EmailVerificationToken.token_hash == hash_token(token)))
  if not token_row or token_row.used_at or as_utc(token_row.expires_at) <= utc_now():
    raise AppError(422, "INVALID_TOKEN", "Verification token is invalid or expired.")
  user = db.get(User, token_row.user_id)
  if not user:
    raise AppError(422, "INVALID_TOKEN", "Verification token is invalid or expired.")
  token_row.used_at = utc_now()
  user.email_verified_at = utc_now()
  write_audit_log(db, event_type="EMAIL_VERIFIED", actor_user_id=user.id, target_user_id=user.id, request_id=request_id)
  return user


def request_password_reset(db: Session, email: str, *, request_id: str | None) -> str | None:
  user = get_user_by_email(db, email)
  if not user:
    return None
  token = new_token()
  db.add(PasswordResetToken(user_id=user.id, token_hash=hash_token(token), expires_at=utc_now() + timedelta(minutes=30)))
  write_audit_log(
    db,
    event_type="PASSWORD_RESET_REQUESTED",
    actor_user_id=user.id,
    target_user_id=user.id,
    request_id=request_id,
    metadata={"password_reset_token_dev": token},
  )
  return token


def confirm_password_reset(db: Session, token: str, password: str, *, request_id: str | None) -> User:
  token_row = db.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash == hash_token(token)))
  if not token_row or token_row.used_at or as_utc(token_row.expires_at) <= utc_now():
    raise AppError(422, "INVALID_TOKEN", "Password reset token is invalid or expired.")
  user = db.get(User, token_row.user_id)
  if not user:
    raise AppError(422, "INVALID_TOKEN", "Password reset token is invalid or expired.")
  token_row.used_at = utc_now()
  user.password_hash = hash_password(password)
  db.query(AuthSession).filter(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None)).update(
    {"revoked_at": utc_now(), "revoked_reason": "PASSWORD_RESET"}
  )
  write_audit_log(db, event_type="PASSWORD_RESET_COMPLETED", actor_user_id=user.id, target_user_id=user.id, request_id=request_id)
  return user
