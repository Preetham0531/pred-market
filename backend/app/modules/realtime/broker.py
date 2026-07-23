import asyncio
import json
import time
from contextlib import suppress
from uuid import uuid4

from redis.asyncio import Redis

from app.core.config import settings
from app.modules.realtime.manager import manager

BROKER_CHANNEL = "pred-market:realtime"


class RealtimeBroker:
  def __init__(self) -> None:
    self.instance_id = uuid4().hex
    self.redis: Redis | None = None
    self.listener_task: asyncio.Task | None = None
    self.heartbeat_task: asyncio.Task | None = None

  async def start(self) -> None:
    self.redis = Redis.from_url(settings.redis_url, decode_responses=True)
    self.listener_task = asyncio.create_task(self._listen())
    self.heartbeat_task = asyncio.create_task(self._heartbeat())

  async def stop(self) -> None:
    for task in (self.listener_task, self.heartbeat_task):
      if task:
        task.cancel()
        with suppress(asyncio.CancelledError):
          await task
    if self.redis:
      await self.redis.aclose()

  async def publish(self, channel: str, payload: dict) -> None:
    if not self.redis:
      return
    message = json.dumps({"source": self.instance_id, "channel": channel, "payload": payload})
    try:
      await self.redis.publish(BROKER_CHANNEL, message)
    except Exception:
      return

  async def _listen(self) -> None:
    while True:
      try:
        if not self.redis:
          await asyncio.sleep(1)
          continue
        async with self.redis.pubsub() as pubsub:
          await pubsub.subscribe(BROKER_CHANNEL)
          async for message in pubsub.listen():
            if message.get("type") != "message":
              continue
            parsed = json.loads(message["data"])
            if parsed.get("source") == self.instance_id:
              continue
            await manager.publish(parsed["channel"], parsed["payload"])
      except asyncio.CancelledError:
        raise
      except Exception:
        await asyncio.sleep(1)

  async def _heartbeat(self) -> None:
    while True:
      await asyncio.sleep(15)
      sequence = int(time.time() * 1000)
      if self.redis:
        try:
          sequence = int(await self.redis.incr("pred-market:heartbeat-sequence"))
        except Exception:
          pass
      await manager.publish_all(
        {
          "event_type": "heartbeat",
          "sequence": sequence,
          "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
          "payload": {},
        }
      )


broker = RealtimeBroker()
