from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.core.rate_limit import check_rate_limit
from app.core.security import expires_in, utc_now
from app.db.session import get_db
from app.modules.auth.dependencies import AuthContext, get_auth_context, get_current_user
from app.modules.auth.mfa import (
  active_factor,
  begin_totp_setup,
  confirm_totp_setup,
  create_challenge,
  disable_factor,
  mfa_status,
  regenerate_recovery_codes,
  verify_challenge,
)
from app.modules.auth.schemas import (
  AcceptedResponse,
  AuthMeResponse,
  AuthResponse,
  EmailRequest,
  MfaChallengeResponse,
  MfaCodeRequest,
  MfaConfirmResponse,
  MfaDisableRequest,
  MfaStatusResponse,
  PasswordResetConfirmRequest,
  SignInRequest,
  SignUpRequest,
  TokenRequest,
  TotpSetupResponse,
  UserResponse,
  WsTicketResponse,
)
from app.modules.auth.service import (
  auth_me_response,
  complete_sign_in,
  create_access_token_for_session,
  confirm_email_verification,
  confirm_password_reset,
  get_session_by_token,
  refresh_session,
  request_email_verification,
  request_password_reset,
  revoke_session,
  sign_up,
  user_to_response,
  roles_for_user,
  verify_sign_in_credentials,
)
from app.modules.realtime.tickets import create_ws_ticket
from app.modules.users.models import User

router = APIRouter()


def set_auth_cookies(response: Response, access_token: str, refresh_token: str, csrf_token: str) -> None:
  response.set_cookie(
    settings.access_cookie_name,
    access_token,
    httponly=True,
    secure=settings.cookie_secure,
    samesite="lax",
    max_age=settings.access_token_ttl_seconds,
    path="/",
  )
  response.set_cookie(
    settings.refresh_cookie_name,
    refresh_token,
    httponly=True,
    secure=settings.cookie_secure,
    samesite="lax",
    max_age=settings.session_ttl_seconds,
    path="/",
  )
  response.set_cookie(
    settings.csrf_cookie_name,
    csrf_token,
    httponly=False,
    secure=settings.cookie_secure,
    samesite="lax",
    max_age=settings.session_ttl_seconds,
    path="/",
  )


def set_access_cookie(response: Response, access_token: str) -> None:
  response.set_cookie(
    settings.access_cookie_name,
    access_token,
    httponly=True,
    secure=settings.cookie_secure,
    samesite="lax",
    max_age=settings.access_token_ttl_seconds,
    path="/",
  )


def set_mfa_challenge_cookie(response: Response, challenge: str) -> None:
  response.set_cookie(
    settings.mfa_challenge_cookie_name,
    challenge,
    httponly=True,
    secure=settings.cookie_secure,
    samesite="lax",
    max_age=settings.mfa_challenge_ttl_seconds,
    path="/api/v1/auth/mfa",
  )


def clear_mfa_challenge_cookie(response: Response) -> None:
  response.delete_cookie(settings.mfa_challenge_cookie_name, path="/api/v1/auth/mfa")


def clear_auth_cookies(response: Response) -> None:
  response.delete_cookie(settings.access_cookie_name, path="/")
  response.delete_cookie(settings.refresh_cookie_name, path="/")
  response.delete_cookie(settings.csrf_cookie_name, path="/")
  response.delete_cookie("pm_access_token", path="/")
  response.delete_cookie("pm_refresh_token", path="/")
  response.delete_cookie("pm_csrf_token", path="/")
  clear_mfa_challenge_cookie(response)


def request_meta(request: Request) -> tuple[str | None, str | None, str | None]:
  return (
    getattr(request.state, "request_id", None),
    request.headers.get("user-agent"),
    request.client.host if request.client else None,
  )


@router.post("/sign-up", response_model=AuthResponse, status_code=201)
def sign_up_endpoint(payload: SignUpRequest, request: Request, response: Response, db: Session = Depends(get_db)):
  if not settings.public_signup_enabled:
    raise AppError(403, "SIGNUP_DISABLED", "Public account creation is currently disabled.")
  if not payload.terms_acceptance:
    raise AppError(422, "TERMS_REQUIRED", "Terms acceptance is required.")
  request_id, user_agent, ip = request_meta(request)
  check_rate_limit(key=f"auth:signup:ip:{ip or 'unknown'}", limit=20, window_seconds=60)
  check_rate_limit(key=f"auth:signup:email:{str(payload.email).lower()}", limit=5, window_seconds=300)
  user, access_token, refresh_token, csrf_token = sign_up(
    db,
    email=str(payload.email),
    password=payload.password,
    display_name=payload.display_name,
    jurisdiction_hint=payload.jurisdiction_hint,
    request_id=request_id,
    user_agent=user_agent,
    ip=ip,
  )
  db.commit()
  set_auth_cookies(response, access_token, refresh_token, csrf_token)
  return {"user": user_to_response(user), "csrf_token": csrf_token}


@router.post("/sign-in", response_model=AuthResponse | MfaChallengeResponse)
def sign_in_endpoint(payload: SignInRequest, request: Request, response: Response, db: Session = Depends(get_db)):
  request_id, user_agent, ip = request_meta(request)
  check_rate_limit(key=f"auth:signin:ip:{ip or 'unknown'}", limit=30, window_seconds=60)
  check_rate_limit(key=f"auth:signin:email:{str(payload.email).lower()}", limit=15, window_seconds=300)
  user = verify_sign_in_credentials(
    db,
    email=str(payload.email),
    password=payload.password,
    request_id=request_id,
    user_agent=user_agent,
    ip=ip,
  )
  roles = roles_for_user(user)
  if active_factor(db, user.id):
    challenge = create_challenge(user, request_id=request_id, user_agent=user_agent)
    db.commit()
    set_mfa_challenge_cookie(response, challenge)
    response.status_code = 202
    return {"mfa_required": True, "expires_in_seconds": settings.mfa_challenge_ttl_seconds}

  user, access_token, refresh_token, csrf_token = complete_sign_in(
    db,
    user=user,
    request_id=request_id,
    user_agent=user_agent,
    ip=ip,
  )
  db.commit()
  set_auth_cookies(response, access_token, refresh_token, csrf_token)
  return {
    "user": user_to_response(user),
    "csrf_token": csrf_token,
    "mfa_setup_required": settings.admin_mfa_required and "ADMIN" in roles,
  }


@router.post("/sign-out", response_model=AcceptedResponse)
def sign_out_endpoint(request: Request, response: Response, db: Session = Depends(get_db)):
  session = get_session_by_token(db, request.cookies.get(settings.refresh_cookie_name))
  if session:
    revoke_session(db, session, reason="SIGN_OUT", request_id=getattr(request.state, "request_id", None))
    db.commit()
  clear_auth_cookies(response)
  return {"status": "accepted", "message": "Signed out."}


@router.post("/refresh", response_model=AuthResponse)
def refresh_endpoint(request: Request, response: Response, db: Session = Depends(get_db)):
  session = get_session_by_token(db, request.cookies.get(settings.refresh_cookie_name))
  if not session:
    raise AppError(401, "UNAUTHENTICATED", "Session is not active.")
  user, access_token, refresh_token, csrf_token = refresh_session(db, session, request_id=getattr(request.state, "request_id", None))
  db.commit()
  set_auth_cookies(response, access_token, refresh_token, csrf_token)
  return {"user": user_to_response(user), "csrf_token": csrf_token}


@router.get("/me", response_model=AuthMeResponse)
def me_endpoint(context = Depends(get_auth_context)):
  return auth_me_response(
    effective_user=context.effective_user,
    actor_user=context.actor_user,
    db=context.db,
    session=context.session,
    impersonation=context.impersonation,
  )


@router.get("/mfa/status", response_model=MfaStatusResponse)
def mfa_status_endpoint(context: AuthContext = Depends(get_auth_context)):
  return mfa_status(context.db, context.actor_user, session_verified=context.session.mfa_verified_at is not None)


@router.post("/mfa/totp/setup", response_model=TotpSetupResponse)
def mfa_totp_setup_endpoint(request: Request, context: AuthContext = Depends(get_auth_context)):
  result = begin_totp_setup(context.db, context.actor_user, request_id=getattr(request.state, "request_id", None))
  context.db.commit()
  return result


@router.post("/mfa/totp/confirm", response_model=MfaConfirmResponse)
def mfa_totp_confirm_endpoint(
  payload: MfaCodeRequest,
  request: Request,
  response: Response,
  context: AuthContext = Depends(get_auth_context),
):
  _, recovery_codes = confirm_totp_setup(
    context.db,
    context.actor_user,
    payload.code,
    request_id=getattr(request.state, "request_id", None),
  )
  context.session.mfa_verified_at = utc_now()
  context.session.mfa_method = "TOTP"
  access_token = create_access_token_for_session(context.db, context.session)
  context.db.commit()
  set_access_cookie(response, access_token)
  return {"status": "confirmed", "recovery_codes": recovery_codes}


@router.post("/mfa/challenge/verify", response_model=AuthResponse)
def mfa_challenge_verify_endpoint(
  payload: MfaCodeRequest,
  request: Request,
  response: Response,
  db: Session = Depends(get_db),
):
  verified = verify_challenge(db, request.cookies.get(settings.mfa_challenge_cookie_name), payload.code)
  request_id, user_agent, ip = request_meta(request)
  user, access_token, refresh_token, csrf_token = complete_sign_in(
    db,
    user=verified.user,
    request_id=request_id,
    user_agent=user_agent,
    ip=ip,
    mfa_method=verified.method,
  )
  db.commit()
  clear_mfa_challenge_cookie(response)
  set_auth_cookies(response, access_token, refresh_token, csrf_token)
  return {"user": user_to_response(user), "csrf_token": csrf_token, "mfa_setup_required": False}


@router.post("/mfa/recovery-codes/regenerate", response_model=MfaConfirmResponse)
def mfa_recovery_codes_regenerate_endpoint(
  payload: MfaCodeRequest,
  request: Request,
  context: AuthContext = Depends(get_auth_context),
):
  codes = regenerate_recovery_codes(
    context.db,
    context.actor_user,
    payload.code,
    request_id=getattr(request.state, "request_id", None),
  )
  context.db.commit()
  return {"status": "regenerated", "recovery_codes": codes}


@router.delete("/mfa/factors/{factor_id}", response_model=AcceptedResponse)
def mfa_factor_delete_endpoint(
  factor_id: str,
  payload: MfaDisableRequest,
  request: Request,
  context: AuthContext = Depends(get_auth_context),
):
  disable_factor(
    context.db,
    context.actor_user,
    factor_id,
    payload.code,
    request_id=getattr(request.state, "request_id", None),
  )
  context.db.commit()
  return {"status": "accepted", "message": "Authenticator factor removed."}


@router.post("/verify-email/request", response_model=AcceptedResponse)
def verify_email_request_endpoint(
  request: Request,
  user: User = Depends(get_current_user),
  db: Session = Depends(get_db),
):
  request_email_verification(db, user, request_id=getattr(request.state, "request_id", None))
  db.commit()
  return {"status": "accepted", "message": "If delivery is configured, a verification email has been sent."}


@router.post("/verify-email/confirm", response_model=UserResponse)
def verify_email_confirm_endpoint(payload: TokenRequest, request: Request, db: Session = Depends(get_db)):
  user = confirm_email_verification(db, payload.token, request_id=getattr(request.state, "request_id", None))
  db.commit()
  return user_to_response(user)


@router.post("/password-reset/request", response_model=AcceptedResponse)
def password_reset_request_endpoint(payload: EmailRequest, request: Request, db: Session = Depends(get_db)):
  request_id, _, ip = request_meta(request)
  check_rate_limit(key=f"auth:password-reset:ip:{ip or 'unknown'}", limit=10, window_seconds=300)
  check_rate_limit(key=f"auth:password-reset:email:{str(payload.email).lower()}", limit=3, window_seconds=900)
  request_password_reset(db, str(payload.email), request_id=request_id)
  db.commit()
  return {"status": "accepted", "message": "If the account exists and delivery is configured, a reset email has been sent."}


@router.post("/password-reset/confirm", response_model=UserResponse)
def password_reset_confirm_endpoint(payload: PasswordResetConfirmRequest, request: Request, db: Session = Depends(get_db)):
  user = confirm_password_reset(db, payload.token, payload.password, request_id=getattr(request.state, "request_id", None))
  db.commit()
  return user_to_response(user)


@router.post("/ws-ticket", response_model=WsTicketResponse)
def ws_ticket_endpoint(context: AuthContext = Depends(get_auth_context)):
  roles = roles_for_user(context.actor_user)
  if settings.admin_mfa_required and "ADMIN" in roles and context.session.mfa_verified_at is None:
    roles = [role for role in roles if role != "ADMIN"]
  return {"ticket": create_ws_ticket(context.effective_user.id, roles), "expires_at": expires_in(60)}
