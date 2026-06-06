"""RelayChatService testlari (fakeredis + soxta bot)."""

from __future__ import annotations

import uuid
from types import SimpleNamespace

import fakeredis.aioredis
import pytest

from bot.services import redis_client
from bot.services.chat_service import RelayChatService


class FakeBot:
    def __init__(self):
        self.copied: list[dict] = []

    async def copy_message(self, chat_id, from_chat_id, message_id):
        self.copied.append(
            {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id}
        )


def _fake_message(user_id: int, message_id: int = 1):
    return SimpleNamespace(
        chat=SimpleNamespace(id=user_id),
        message_id=message_id,
    )


def _session(mentor_id=10, mentee_id=11):
    return SimpleNamespace(id=uuid.uuid4(), mentor_id=mentor_id, mentee_id=mentee_id)


@pytest.fixture(autouse=True)
def _fake_redis():
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    redis_client.set_redis(client)
    yield client
    redis_client._redis = None


@pytest.mark.asyncio
async def test_open_channel_sets_mapping():
    bot = FakeBot()
    svc = RelayChatService(bot)
    session = _session()
    sid = await svc.open_channel(session)

    assert sid == str(session.id)
    assert await svc.get_peer(sid, 10) == 11
    assert await svc.get_peer(sid, 11) == 10
    assert await svc.get_peer(sid, 999) is None


@pytest.mark.asyncio
async def test_relay_forwards_to_peer():
    bot = FakeBot()
    svc = RelayChatService(bot)
    session = _session()
    sid = await svc.open_channel(session)

    ok = await svc.relay(sid, from_user_id=10, message=_fake_message(10, 42))
    assert ok is True
    assert len(bot.copied) == 1
    # Mentor (10) yozdi -> mentee (11) ga uzatildi
    assert bot.copied[0]["chat_id"] == 11
    assert bot.copied[0]["message_id"] == 42


@pytest.mark.asyncio
async def test_relay_inactive_after_close():
    bot = FakeBot()
    svc = RelayChatService(bot)
    session = _session()
    sid = await svc.open_channel(session)
    await svc.close_channel(session)

    ok = await svc.relay(sid, from_user_id=10, message=_fake_message(10))
    assert ok is False
    assert bot.copied == []
    assert await svc.get_session_for_user(10) is None


@pytest.mark.asyncio
async def test_get_session_for_user():
    bot = FakeBot()
    svc = RelayChatService(bot)
    session = _session(mentor_id=20, mentee_id=21)
    sid = await svc.open_channel(session)

    assert await svc.get_session_for_user(20) == sid
    assert await svc.get_session_for_user(21) == sid
    assert await svc.get_session_for_user(99) is None
