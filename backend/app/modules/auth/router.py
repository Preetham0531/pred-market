from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.core.rate_limit import check_rate_limit
from app.core.security import expires_in
from app.db.session import get_db
from app.modules.auth.dependencies import get_auth_context, get_current_user
from app.modules.auth.schemas import (
  AcceptedResponse,
  AuthMeResponse,
  AuthResponse,
  EmailRequest,
  PasswordResetConfirmRequest,
  SignInRequest,
  SignUpRequest,
  TokenRequest,
  UserResponse,
  WsTicketResponse,
)
from app.modules.auth.service import (
  auth_me_response,
  confirm_email_verification,
  confirm_password_reset,
  get_session_by_token,
  refresh_session,
  request_email_verification,
  request_password_reset,
  revoke_session,
  sign_in,
  sign_up,
  user_to_response,
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


def clear_auth_cookies(response: Response) -> None:
  response.delete_cookie(settings.access_cookie_name, path="/")
  response.delete_cookie(settings.refresh_cookie_name, path="/")
  response.delete_cookie(settings.csrf_cookie_name, path="/")
  response.delete_cookie("pm_access_token", path="/")
  response.delete_cookie("pm_refresh_token", path="/")
  response.delete_cookie("pm_csrf_token", path="/")


def request_meta(request: Request) -> tuple[str | None, str | None, str | None]:
  return (
    getattr(request.state, "request_id", None),
    request.headers.get("user-agent"),
    request.client.host if request.client else None,
  )


@router.post("/sign-up", response_model=AuthResponse, status_code=201)
def sign_up_endpoint(payload: SignUpRequest, request: Request, response: Response, db: Session = Depends(get_db)):
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


@router.post("/sign-in", response_model=AuthResponse)
def sign_in_endpoint(payload: SignInRequest, request: Request, response: Response, db: Session = Depends(get_db)):
  request_id, user_agent, ip = request_meta(request)
  check_rate_limit(key=f"auth:signin:ip:{ip or 'unknown'}", limit=30, window_seconds=60)
  check_rate_limit(key=f"auth:signin:email:{str(payload.email).lower()}", limit=15, window_seconds=300)
  user, access_token, refresh_token, csrf_token = sign_in(
    db,
    email=str(payload.email),
    password=payload.password,
    request_id=request_id,
    user_agent=user_agent,
    ip=ip,
  )
  db.commit()
  set_auth_cookies(response, access_token, refresh_token, csrf_token)
  return {"user": user_to_response(user), "csrf_token": csrf_token}


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
    impersonation=context.impersonation,
  )


@router.post("/verify-email/request", response_model=AcceptedResponse)
def verify_email_request_endpoint(
  request: Request,
  user: User = Depends(get_current_user),
  db: Session = Depends(get_db),
):
  request_email_verification(db, user, request_id=getattr(request.state, "request_id", None))
  db.commit()
  return {"status": "accepted", "message": "Verification token created. Delivery is stubbed in development."}


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
  return {"status": "accepted", "message": "If the account exists, a reset token was created. Delivery is stubbed in development."}


@router.post("/password-reset/confirm", response_model=UserResponse)
def password_reset_confirm_endpoint(payload: PasswordResetConfirmRequest, request: Request, db: Session = Depends(get_db)):
  user = confirm_password_reset(db, payload.token, payload.password, request_id=getattr(request.state, "request_id", None))
  db.commit()
  return user_to_response(user)


@router.post("/ws-ticket", response_model=WsTicketResponse)
def ws_ticket_endpoint(user: User = Depends(get_current_user)):
  return {"ticket": create_ws_ticket(user.id, [role.role for role in user.roles]), "expires_at": expires_in(60)}
