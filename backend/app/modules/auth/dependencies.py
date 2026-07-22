from collections.abc import Callable
from dataclasses import dataclass

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.core.security import decode_jwt
from app.db.session import get_db
from app.modules.audit.service import write_audit_log
from app.modules.auth.models import AdminImpersonationSession, AuthSession
from app.modules.auth.service import get_active_impersonation, get_session_by_id, roles_for_user
from app.modules.users.models import User


@dataclass(frozen=True)
class AuthContext:
  db: Session
  session: AuthSession
  actor_user: User
  effective_user: User
  impersonation: AdminImpersonationSession | None = None

  @property
  def actor_roles(self) -> set[str]:
    return set(roles_for_user(self.actor_user))

  @property
  def effective_roles(self) -> set[str]:
    return set(roles_for_user(self.effective_user))

  @property
  def is_read_only_impersonation(self) -> bool:
    return self.impersonation is not None and self.impersonation.mode == "READ_ONLY"


def get_auth_context(request: Request, db: Session = Depends(get_db)) -> AuthContext:
  token = request.cookies.get(settings.access_cookie_name)
  if not token:
    raise AppError(401, "UNAUTHENTICATED", "Sign in is required.")
  claims = decode_jwt(token)
  session = get_session_by_id(db, claims.get("sid"))
  if not session:
    raise AppError(401, "UNAUTHENTICATED", "Sign in is required.")
  actor_user = session.user
  if actor_user.status != "ACTIVE":
    raise AppError(403, "ACCOUNT_UNAVAILABLE", "This account is not active.")
  impersonation = get_active_impersonation(db, session.id)
  effective_user = actor_user
  if impersonation:
    effective_user = impersonation.target_user
    if "ADMIN" not in set(roles_for_user(actor_user)):
      raise AppError(403, "FORBIDDEN", "Impersonation actor is not authorized.")
    if effective_user.status != "ACTIVE":
      raise AppError(403, "ACCOUNT_UNAVAILABLE", "This account is not active.")
  return AuthContext(db=db, session=session, actor_user=actor_user, effective_user=effective_user, impersonation=impersonation)


def get_current_user(context: AuthContext = Depends(get_auth_context)) -> User:
  return context.effective_user


def get_current_user_for_write(
  request: Request,
  context: AuthContext = Depends(get_auth_context),
  db: Session = Depends(get_db),
) -> User:
  if settings.email_verification_required and context.effective_user.email_verified_at is None:
    raise AppError(403, "EMAIL_VERIFICATION_REQUIRED", "Verify your email before making account or trading changes.")
  if context.is_read_only_impersonation:
    write_audit_log(
      db,
      event_type="IMPERSONATION_WRITE_BLOCKED",
      actor_user_id=context.actor_user.id,
      target_user_id=context.effective_user.id,
      request_id=getattr(request.state, "request_id", None),
      metadata={"path": request.url.path, "method": request.method, "impersonation_session_id": context.impersonation.id if context.impersonation else None},
    )
    db.commit()
    raise AppError(403, "IMPERSONATION_READ_ONLY", "Admin user view is read-only.")
  return context.effective_user


def require_role(role: str) -> Callable[[User], User]:
  def dependency(context: AuthContext = Depends(get_auth_context)) -> User:
    roles = context.actor_roles if role == "ADMIN" else context.effective_roles
    if role == "CHECKER":
      roles = context.actor_roles
      role_to_check = "ADMIN"
    else:
      role_to_check = role
    if role_to_check not in roles:
      raise AppError(403, "FORBIDDEN", "You do not have permission to access this resource.")
    if role_to_check == "ADMIN" and settings.admin_mfa_required and context.session.mfa_verified_at is None:
      write_audit_log(
        context.db,
        event_type="ADMIN_MFA_REQUIRED",
        actor_user_id=context.actor_user.id,
        target_user_id=context.actor_user.id,
        metadata={"session_id": context.session.id},
      )
      context.db.commit()
      raise AppError(403, "MFA_REQUIRED", "Authenticator verification is required for admin access.")
    return context.actor_user if role_to_check == "ADMIN" else context.effective_user

  return dependency


require_admin = require_role("ADMIN")
require_checker = require_role("CHECKER")
