from datetime import datetime

from pydantic import BaseModel

from app.modules.analytics.schemas import RecomputeResponse
from app.modules.auth.schemas import AuthMeResponse


class AdminReviewResponse(BaseModel):
  id: str
  suggestion_id: str | None
  draft_id: str | None = None
  market_id: str | None
  title: str
  category: str
  status: str
  risk: str
  submitted_by: str
  created_at: datetime
  resolved_at: datetime | None


class AdminReviewList(BaseModel):
  items: list[AdminReviewResponse]
  next_cursor: str | None = None


class AdminActionResponse(BaseModel):
  status: str
  market_id: str


class AdminUserResponse(BaseModel):
  id: str
  email: str
  display_name: str | None
  status: str
  roles: list[str]


class AdminUserList(BaseModel):
  items: list[AdminUserResponse]
  next_cursor: str | None = None


class ImpersonationStartRequest(BaseModel):
  target_user_id: str
  reason: str


class ImpersonationAuthResponse(AuthMeResponse):
  pass
