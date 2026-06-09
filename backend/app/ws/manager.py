"""WebSocket connection manager with Redis pub/sub fan-out.

Keeps a per-slot set of local connections and bridges cross-instance events
through Redis so multiple API workers stay in sync.
"""
from __future__ import annotations

import asyncio
import json
from collections import defaultdict

from fastapi import WebSocket

from app.services.cache import redis_client


def _channel(slot_id: str) -> str:
    return f"slot:{slot_id}"


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._tasks: dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    async def connect(self, slot_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[slot_id].add(websocket)
            if slot_id not in self._tasks:
                self._tasks[slot_id] = asyncio.create_task(
                    self._subscribe(slot_id)
                )

    async def disconnect(self, slot_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            conns = self._connections.get(slot_id)
            if conns:
                conns.discard(websocket)
                if not conns:
                    self._connections.pop(slot_id, None)
                    task = self._tasks.pop(slot_id, None)
                    if task:
                        task.cancel()

    async def publish(self, slot_id: str, event: dict) -> None:
        """Publish an event to all instances via Redis."""
        await redis_client.publish(_channel(slot_id), json.dumps(event))

    async def _broadcast_local(self, slot_id: str, message: str) -> None:
        for ws in list(self._connections.get(slot_id, set())):
            try:
                await ws.send_text(message)
            except Exception:
                await self.disconnect(slot_id, ws)

    async def _subscribe(self, slot_id: str) -> None:
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(_channel(slot_id))
        try:
            async for message in pubsub.listen():
                if message.get("type") == "message":
                    await self._broadcast_local(slot_id, message["data"])
        except asyncio.CancelledError:
            pass
        finally:
            await pubsub.unsubscribe(_channel(slot_id))
            await pubsub.aclose()


manager = ConnectionManager()
