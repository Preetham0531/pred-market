from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import settings
from app.modules.realtime.manager import manager
from app.modules.realtime.tickets import consume_ws_ticket

router = APIRouter()


def public_market_channel(channel: str) -> bool:
  return channel.startswith(("market.order_book.", "market.trades.", "market.ticker.", "market.status."))


def authorized_channel(channel: str, auth: dict[str, object] | None) -> bool:
  if public_market_channel(channel):
    return True
  if channel in {"user.orders", "user.positions", "user.wallet", "user.notifications"}:
    return bool(auth and auth.get("user_id"))
  if channel in {"admin.review_queue", "admin.risk_alerts", "admin.settlement_status"}:
    return bool(auth and "ADMIN" in set(auth.get("roles") or []))
  return False


def concrete_channel(channel: str, auth: dict[str, object] | None) -> str:
  if channel.startswith("user."):
    return f"{channel}.{auth.get('user_id')}"
  return channel


@router.websocket("/ws/v1")
async def websocket_endpoint(websocket: WebSocket):
  origin = websocket.headers.get("origin")
  allowed_origins = set(settings.cors_origin_list)
  if settings.environment == "development":
    allowed_origins.update({"http://localhost:3000", "http://127.0.0.1:3000", "http://testserver"})
  if origin and origin not in allowed_origins:
    await websocket.close(code=1008, reason="Origin is not allowed.")
    return
  ticket = websocket.query_params.get("ticket")
  auth = consume_ws_ticket(ticket)
  await websocket.accept()
  try:
    while True:
      message = await websocket.receive_json()
      if message.get("type") != "subscribe":
        await websocket.send_json({"type": "error", "code": "UNSUPPORTED_MESSAGE", "message": "Only subscribe messages are supported."})
        continue
      channel = str(message.get("channel") or "")
      market_id = message.get("market_id")
      if market_id and channel.startswith("market."):
        channel = f"{channel}.{market_id}"
      if not authorized_channel(channel, auth):
        await websocket.send_json({"type": "error", "code": "FORBIDDEN", "message": "Channel is not available for this connection."})
        continue
      resolved = concrete_channel(channel, auth)
      await manager.subscribe(websocket, resolved)
      await websocket.send_json({"type": "subscribed", "channel": channel, "resolved_channel": resolved, "snapshot_sequence": None})
  except WebSocketDisconnect:
    await manager.unsubscribe_all(websocket)
  except Exception:
    await manager.unsubscribe_all(websocket)
