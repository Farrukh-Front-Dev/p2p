"""WebSocket endpoint for live slot sessions."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.security import decode_token
from app.db.base import AsyncSessionLocal
from app.db.models.slot import Slot
from app.db.models.user import User
from app.services import slot_service
from app.ws.manager import manager

router = APIRouter()


async def _authenticate(token: str | None) -> User | None:
    if not token:
        return None
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        return None
    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError, TypeError):
        return None
    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_id)
        return user if user and user.is_active else None


@router.websocket("/ws/slot/{slot_id}")
async def slot_websocket(
    websocket: WebSocket,
    slot_id: str,
    token: str | None = Query(None),
):
    user = await _authenticate(token)
    if user is None:
        await websocket.close(code=4401)
        return

    await manager.connect(slot_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await _handle_client_event(slot_id, user, data)
    except WebSocketDisconnect:
        await manager.disconnect(slot_id, websocket)
    except Exception:
        await manager.disconnect(slot_id, websocket)


async def _handle_client_event(slot_id: str, user: User, data: dict) -> None:
    event = data.get("event")
    sid = uuid.UUID(slot_id)

    async with AsyncSessionLocal() as db:
        slot = await db.get(Slot, sid)
        if slot is None:
            return

        if event == "client.start":
            slot = await slot_service.start_slot(db, slot, user)
            await db.commit()
            who = "reviewer" if user.id == slot.reviewer_id else "reviewee"
            await manager.publish(slot_id, {"event": "slot.start", "who": who})
            if slot.reviewer_started and slot.reviewee_started:
                await manager.publish(
                    slot_id,
                    {
                        "event": "slot.both_started",
                        "reviewer_link": _tg_link(slot.reviewee),
                        "reviewee_link": _tg_link(slot.reviewer),
                    },
                )
        elif event == "client.finish":
            slot = await slot_service.finish_slot(db, slot, user)
            await db.commit()
            who = "reviewer" if user.id == slot.reviewer_id else "reviewee"
            await manager.publish(slot_id, {"event": "slot.finish", "who": who})
            if slot.status == "completed":
                await manager.publish(
                    slot_id,
                    {
                        "event": "slot.both_finished",
                        "duration_minutes": slot.duration_minutes,
                    },
                )
        elif event == "client.absent":
            slot = await slot_service.mark_absent(db, slot, user)
            await db.commit()
            await manager.publish(
                slot_id, {"event": "slot.absent", "by": str(user.id)}
            )


def _tg_link(other: User | None) -> str | None:
    if other and other.telegram_username:
        return f"https://t.me/{other.telegram_username}"
    return None
