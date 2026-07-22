from __future__ import annotations

import html

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.audit.service import write_audit_log
from app.modules.users.models import User

RESEND_ENDPOINT = "https://api.resend.com/emails"


def _send_email(*, to: str, subject: str, text: str, html_body: str) -> str | None:
  if not settings.email_delivery_enabled or not settings.resend_api_key or not settings.resend_from:
    return None
  response = httpx.post(
    RESEND_ENDPOINT,
    headers={"Authorization": f"Bearer {settings.resend_api_key}", "Content-Type": "application/json"},
    json={"from": settings.resend_from, "to": [to], "subject": subject, "text": text, "html": html_body},
    timeout=10.0,
  )
  response.raise_for_status()
  payload = response.json()
  return str(payload.get("id") or "") or None


def _deliver(
  db: Session,
  *,
  user: User,
  event_name: str,
  subject: str,
  text: str,
  html_body: str,
  request_id: str | None,
) -> None:
  try:
    provider_id = _send_email(to=user.email, subject=subject, text=text, html_body=html_body)
    write_audit_log(
      db,
      event_type=f"{event_name}_EMAIL_QUEUED" if provider_id else f"{event_name}_EMAIL_SKIPPED",
      actor_user_id=user.id,
      target_user_id=user.id,
      request_id=request_id,
      metadata={"provider": "RESEND", "provider_message_id": provider_id} if provider_id else {"provider": "DISABLED"},
    )
  except (httpx.HTTPError, ValueError):
    write_audit_log(
      db,
      event_type=f"{event_name}_EMAIL_FAILED",
      actor_user_id=user.id,
      target_user_id=user.id,
      request_id=request_id,
      metadata={"provider": "RESEND"},
    )


def send_verification_email(db: Session, user: User, token: str, *, request_id: str | None) -> None:
  url = f"{settings.frontend_base_url.rstrip('/')}/verify-email?token={token}"
  safe_url = html.escape(url, quote=True)
  _deliver(
    db,
    user=user,
    event_name="VERIFICATION",
    subject="Verify your Pred-Market email",
    text=f"Verify your email: {url}",
    html_body=f'<p>Verify your Pred-Market email.</p><p><a href="{safe_url}">Verify email</a></p>',
    request_id=request_id,
  )


def send_password_reset_email(db: Session, user: User, token: str, *, request_id: str | None) -> None:
  url = f"{settings.frontend_base_url.rstrip('/')}/reset-password?token={token}"
  safe_url = html.escape(url, quote=True)
  _deliver(
    db,
    user=user,
    event_name="PASSWORD_RESET",
    subject="Reset your Pred-Market password",
    text=f"Reset your password: {url}",
    html_body=f'<p>A password reset was requested for your Pred-Market account.</p><p><a href="{safe_url}">Reset password</a></p>',
    request_id=request_id,
  )
