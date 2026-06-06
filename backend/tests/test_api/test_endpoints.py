"""API endpoint oqimlari testi (TestClient + SQLite)."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from collections.abc import AsyncIterator
from datetime import timedelta
from urllib.parse import urlencode

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bot.api.deps import get_db_session
from bot.api_server import app
from bot.config import settings
from bot.database import models  # noqa: F401
from bot.database.base import Base
from bot.repositories.user_repo import UserRepository
from bot.utils.time_utils import now_local


@pytest_asyncio.fixture
async def maker():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    m = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    yield m
    await engine.dispose()


@pytest.fixture
def client(maker):
    async def _override() -> AsyncIterator[AsyncSession]:
        async with maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _init_data(user: dict) -> str:
    fields = {
        "user": json.dumps(user, separators=(",", ":")),
        "auth_date": str(int(time.time())),
    }
    dcs = "\n".join(f"{k}={fields[k]}" for k in sorted(fields))
    secret = hmac.new(b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)


async def _seed_user(maker, user_id=100, coins=5, **kw):
    async with maker() as db:
        repo = UserRepository(db)
        await repo.create_or_update(
            user_id=user_id,
            username=kw.get("username", f"u{user_id}"),
            school21_login=kw.get("login", f"login{user_id}"),
            nickname=kw.get("nickname", f"nick{user_id}"),
            directions=kw.get("directions", ["python"]),
        )
        if coins != 5:
            await repo.update(user_id, coins=coins)
        await db.commit()


def _token(client, user_id, username="u100"):
    resp = client.post(
        "/api/auth/telegram",
        json={"init_data": _init_data({"id": user_id, "username": username})},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_auth_new_user(client):
    resp = client.post(
        "/api/auth/telegram",
        json={"init_data": _init_data({"id": 999, "first_name": "New"})},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_new_user"] is True
    assert data["access_token"]


def test_auth_invalid_init_data(client):
    resp = client.post("/api/auth/telegram", json={"init_data": "hash=bad&user=x"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_dev_auth_existing_user(client, maker):
    await _seed_user(maker, 100)
    resp = client.post("/api/auth/dev?user_id=100")
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_new_user"] is False
    assert data["user"]["id"] == 100
    assert data["access_token"]


def test_dev_auth_new_user(client):
    resp = client.post("/api/auth/dev?user_id=777")
    assert resp.status_code == 200
    assert resp.json()["is_new_user"] is True


@pytest.mark.asyncio
async def test_me_and_directions(client, maker):
    await _seed_user(maker, 100)
    token = _token(client, 100)

    resp = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == 100
    assert body["xp"] == 0
    assert body["level"] == 1
    assert body["coins"] == 5

    # directions ochiq endpoint
    resp = client.get("/api/directions")
    assert resp.status_code == 200
    assert any(d["id"] == "python" for d in resp.json())


def test_me_requires_auth(client):
    resp = client.get("/api/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_and_book_slot_flow(client, maker):
    await _seed_user(maker, 100)  # mentor
    await _seed_user(maker, 200)  # mentee
    mentor_token = _token(client, 100)
    mentee_token = _token(client, 200, username="u200")

    start = (now_local() + timedelta(hours=2)).replace(microsecond=0)
    end = start + timedelta(hours=3)

    # Mentor slot ochadi
    resp = client.post(
        "/api/slots",
        headers={"Authorization": f"Bearer {mentor_token}"},
        json={
            "direction": "python",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
        },
    )
    assert resp.status_code == 200, resp.text

    # Mentee mavjud slotlarni ko'radi
    resp = client.get(
        "/api/slots?direction=python",
        headers={"Authorization": f"Bearer {mentee_token}"},
    )
    assert resp.status_code == 200
    slots = resp.json()
    assert len(slots) == 1
    slot_id = slots[0]["id"]
    assert slots[0]["is_mine"] is False  # anonimlik

    # Mentee band qiladi (2 soat)
    b_start = start
    b_end = start + timedelta(hours=2)
    resp = client.post(
        f"/api/slots/{slot_id}/book",
        headers={"Authorization": f"Bearer {mentee_token}"},
        json={"start_time": b_start.isoformat(), "end_time": b_end.isoformat()},
    )
    assert resp.status_code == 200, resp.text

    # Mentee coins 4 ga tushdi
    resp = client.get("/api/me", headers={"Authorization": f"Bearer {mentee_token}"})
    assert resp.json()["coins"] == 4


@pytest.mark.asyncio
async def test_book_over_4h_rejected(client, maker):
    await _seed_user(maker, 100)
    await _seed_user(maker, 200)
    mentor_token = _token(client, 100)
    mentee_token = _token(client, 200, username="u200")

    start = (now_local() + timedelta(hours=2)).replace(microsecond=0)
    end = start + timedelta(hours=8)
    resp = client.post(
        "/api/slots",
        headers={"Authorization": f"Bearer {mentor_token}"},
        json={"direction": "python", "start_time": start.isoformat(), "end_time": end.isoformat()},
    )
    slot_id = None
    resp = client.get(
        "/api/slots?direction=python",
        headers={"Authorization": f"Bearer {mentee_token}"},
    )
    slot_id = resp.json()[0]["id"]

    # 5 soat band qilishga urinish — rad etiladi
    resp = client.post(
        f"/api/slots/{slot_id}/book",
        headers={"Authorization": f"Bearer {mentee_token}"},
        json={
            "start_time": start.isoformat(),
            "end_time": (start + timedelta(hours=5)).isoformat(),
        },
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_leaderboard(client, maker):
    await _seed_user(maker, 100)
    async with maker() as db:
        repo = UserRepository(db)
        await repo.update(100, xp=500, level=4, total_taught=3)
        await db.commit()
    token = _token(client, 100)
    resp = client.get("/api/leaderboard", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    board = resp.json()
    assert board[0]["rank"] == 1
    assert board[0]["xp"] == 500
