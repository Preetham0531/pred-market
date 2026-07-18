from typing import Any

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class AppError(HTTPException):
  def __init__(self, status_code: int, code: str, message: str, details: dict[str, Any] | None = None):
    super().__init__(status_code=status_code, detail={"code": code, "message": message, "details": details or {}})


def error_response(status_code: int, code: str, message: str, request_id: str | None, details: dict[str, Any] | None = None):
  return JSONResponse(
    status_code=status_code,
    content={
      "error": {
        "code": code,
        "message": message,
        "request_id": request_id,
        "details": details or {},
      }
    },
  )


async def app_error_handler(request: Request, exc: AppError):
  request_id = getattr(request.state, "request_id", None)
  detail = exc.detail if isinstance(exc.detail, dict) else {}
  return error_response(
    exc.status_code,
    detail.get("code", "APP_ERROR"),
    detail.get("message", "Request failed."),
    request_id,
    detail.get("details", {}),
  )


async def http_error_handler(request: Request, exc: HTTPException):
  request_id = getattr(request.state, "request_id", None)
  if isinstance(exc.detail, dict) and "code" in exc.detail:
    return error_response(
      exc.status_code,
      exc.detail.get("code", "HTTP_ERROR"),
      exc.detail.get("message", "Request failed."),
      request_id,
      exc.detail.get("details", {}),
    )
  return error_response(exc.status_code, "HTTP_ERROR", str(exc.detail), request_id)
