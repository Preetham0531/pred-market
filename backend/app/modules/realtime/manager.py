from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
  def __init__(self) -> None:
    self._channels: dict[str, set[WebSocket]] = defaultdict(set)
    self._socket_channels: dict[WebSocket, set[str]] = defaultdict(set)

  async def subscribe(self, websocket: WebSocket, channel: str) -> None:
    self._channels[channel].add(websocket)
    self._socket_channels[websocket].add(channel)

  async def unsubscribe_all(self, websocket: WebSocket) -> None:
    for channel in self._socket_channels.pop(websocket, set()):
      sockets = self._channels.get(channel)
      if not sockets:
        continue
      sockets.discard(websocket)
      if not sockets:
        self._channels.pop(channel, None)

  async def publish(self, channel: str, payload: dict) -> None:
    stale: list[WebSocket] = []
    for websocket in list(self._channels.get(channel, set())):
      try:
        await websocket.send_json(payload)
      except Exception:
        stale.append(websocket)
    for websocket in stale:
      await self.unsubscribe_all(websocket)

  async def publish_all(self, payload: dict) -> None:
    stale: set[WebSocket] = set()
    for websocket in list(self._socket_channels):
      try:
        await websocket.send_json(payload)
      except Exception:
        stale.add(websocket)
    for websocket in stale:
      await self.unsubscribe_all(websocket)


manager = ConnectionManager()
