from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class SignUpRequest(BaseModel):
  email: EmailStr
  password: str = Field(min_length=8, max_length=256)
  display_name: str | None = Field(default=None, max_length=160)
  terms_acceptance: bool = True
  jurisdiction_hint: str | None = Field(default=None, max_length=16)


class SignInRequest(BaseModel):
  email: EmailStr
  password: str = Field(min_length=1, max_length=256)


class TokenRequest(BaseModel):
  token: str


class EmailRequest(BaseModel):
  email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
  token: str
  password: str = Field(min_length=8, max_length=256)


class UserResponse(BaseModel):
  id: str
  email: EmailStr
  display_name: str | None
  status: str
  roles: list[str]
  email_verified_at: datetime | None
  kyc_status: str
  jurisdiction_code: str | None


class ImpersonationResponse(BaseModel):
  active: bool
  session_id: str
  mode: str
  actor_user_id: str
  target_user_id: str
  started_at: datetime


class AuthMeResponse(BaseModel):
  user: UserResponse
  actor: UserResponse
  impersonation: ImpersonationResponse | None


class AuthResponse(BaseModel):
  user: UserResponse
  csrf_token: str


class AcceptedResponse(BaseModel):
  status: str
  message: str


class WsTicketResponse(BaseModel):
  ticket: str
  expires_at: datetime
