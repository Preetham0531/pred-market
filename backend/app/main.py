from uuid import uuid4
from hmac import compare_digest
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import AppError, app_error_handler, error_response, http_error_handler
from app.core.logging import configure_logging
from app.db.redis import get_redis
from app.db.session import SessionLocal
from app.modules.realtime.router import router as realtime_router
from app.modules.realtime.broker import broker

configure_logging()

@asynccontextmanager
async def lifespan(_: FastAPI):
  await broker.start()
  try:
    yield
  finally:
    await broker.stop()


app = FastAPI(title=settings.app_name, version=settings.version, lifespan=lifespan)

app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.cors_origin_list,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
  request_id = request.headers.get("X-Request-ID", f"req_{uuid4().hex}")
  request.state.request_id = request_id
  response = await call_next(request)
  response.headers["X-Request-ID"] = request_id
  return response


app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(HTTPException, http_error_handler)


def is_allowed_local_origin(origin: str | None) -> bool:
  if not origin:
    return False
  allowed = set(settings.cors_origin_list)
  allowed.update({"http://localhost:3000", "http://127.0.0.1:3000", "http://[::1]:3000"})
  return origin in allowed


def add_cors_headers(response: Response, origin: str | None) -> Response:
  if is_allowed_local_origin(origin):
    response.headers["Access-Control-Allow-Origin"] = origin or ""
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Vary"] = "Origin"
  return response


@app.middleware("http")
async def local_cors_safety_middleware(request: Request, call_next):
  origin = request.headers.get("origin")
  if request.method == "OPTIONS" and is_allowed_local_origin(origin):
    requested_headers = request.headers.get("access-control-request-headers", "content-type,x-csrf-token,idempotency-key")
    response = Response("OK", status_code=200)
    response.headers["Access-Control-Allow-Origin"] = origin or ""
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"
    response.headers["Access-Control-Allow-Headers"] = requested_headers
    response.headers["Access-Control-Max-Age"] = "600"
    response.headers["Vary"] = "Origin"
    return response
  response = await call_next(request)
  return add_cors_headers(response, origin)


CSRF_EXEMPT_PATHS = {
  f"{settings.api_v1_prefix}/auth/sign-in",
  f"{settings.api_v1_prefix}/auth/sign-up",
  f"{settings.api_v1_prefix}/auth/refresh",
  f"{settings.api_v1_prefix}/auth/password-reset/request",
  f"{settings.api_v1_prefix}/auth/password-reset/confirm",
  f"{settings.api_v1_prefix}/auth/verify-email/confirm",
  f"{settings.api_v1_prefix}/auth/mfa/challenge/verify",
}


@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
  if request.method in {"POST", "PUT", "PATCH", "DELETE"} and request.url.path not in CSRF_EXEMPT_PATHS:
    csrf_cookie = request.cookies.get(settings.csrf_cookie_name)
    csrf_header = request.headers.get("X-CSRF-Token")
    has_auth_cookie = request.cookies.get(settings.access_cookie_name) or request.cookies.get(settings.refresh_cookie_name)
    if has_auth_cookie and (not csrf_cookie or not csrf_header or not compare_digest(csrf_cookie, csrf_header)):
      return error_response(
        403,
        "CSRF_TOKEN_INVALID",
        "CSRF token is missing or invalid.",
        getattr(request.state, "request_id", None),
      )
  return await call_next(request)


def health_payload() -> dict[str, str]:
  return {"status": "ok", "service": settings.app_name, "environment": settings.environment}


@app.get("/health")
def root_health():
  return health_payload()


@app.get("/health/live")
def liveness():
  return health_payload()


def dependency_health() -> tuple[str, str]:
  db_status = "ok"
  redis_status = "ok"
  try:
    with SessionLocal() as db:
      db.execute(text("select 1"))
  except Exception:
    db_status = "error"
  try:
    get_redis().ping()
  except Exception:
    redis_status = "error"
  return db_status, redis_status


@app.get("/health/ready")
def readiness():
  db_status, redis_status = dependency_health()
  payload = {**health_payload(), "database": db_status, "redis": redis_status}
  if db_status != "ok" or redis_status != "ok":
    return JSONResponse(status_code=503, content=payload)
  return payload


@app.get(f"{settings.api_v1_prefix}/health")
def api_health():
  db_status, redis_status = dependency_health()
  return {**health_payload(), "database": db_status, "redis": redis_status}


@app.get(f"{settings.api_v1_prefix}/version")
def version():
  return {"version": settings.version, "api_prefix": settings.api_v1_prefix}


app.include_router(api_router, prefix=settings.api_v1_prefix)
app.include_router(realtime_router)
