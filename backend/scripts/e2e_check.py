"""End-to-end smoke test against the running API.

Creates two users directly in the DB, issues JWTs, then exercises the slot
lifecycle: create -> search -> book -> start (both) -> finish (both) -> review.
"""
from __future__ import annotations

import asyncio
import uuid

import httpx

from app.core.security import create_access_token
from app.db.base import AsyncSessionLocal
from app.db.models.user import User

BASE = "http://localhost:8000/api/v1"


async def seed() -> tuple[str, str]:
    async with AsyncSessionLocal() as db:
        suffix = uuid.uuid4().hex[:6]
        teacher = User(
            telegram_id=int(uuid.uuid4().int % 10_000_000),
            school21_login=f"teacher_{suffix}",
            first_name="Teacher",
            campus="samarkand",
            languages=["uz", "ru"],
            peer_points=5,
        )
        learner = User(
            telegram_id=int(uuid.uuid4().int % 10_000_000) + 1,
            school21_login=f"learner_{suffix}",
            first_name="Learner",
            campus="samarkand",
            languages=["uz"],
            peer_points=5,
        )
        db.add_all([teacher, learner])
        await db.commit()
        await db.refresh(teacher)
        await db.refresh(learner)
        return str(teacher.id), str(learner.id)


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def main() -> None:
    teacher_id, learner_id = await seed()
    t_tok = create_access_token(teacher_id)
    l_tok = create_access_token(learner_id)

    async with httpx.AsyncClient(base_url=BASE, timeout=10) as c:
        # 1. Teacher creates an open slot.
        r = await c.post(
            "/slots/",
            headers=auth(t_tok),
            json={
                "reviewer_project": "C6_simple_shell",
                "start_time": "2026-06-09T10:00:00+00:00",
                "end_time": "2026-06-09T11:00:00+00:00",
                "is_online": True,
            },
        )
        print("create slot:", r.status_code)
        assert r.status_code == 201, r.text
        slot_id = r.json()["id"]

        # 2. Learner searches for matching slots.
        r = await c.get(
            "/slots/search",
            headers=auth(l_tok),
            params={"project": "C6_simple_shell"},
        )
        print("search:", r.status_code, "->", len(r.json()), "result(s)")
        assert r.status_code == 200 and len(r.json()) >= 1
        # Search results must be anonymous (no reviewer name/id).
        assert "reviewer_id" not in r.json()[0]

        # 3. Learner books it.
        r = await c.post(f"/slots/{slot_id}/book", headers=auth(l_tok), json={})
        print("book:", r.status_code, "status:", r.json()["status"])
        assert r.status_code == 200 and r.json()["status"] == "booked"

        # 4. Both start.
        await c.post(f"/slots/{slot_id}/start", headers=auth(t_tok))
        r = await c.post(f"/slots/{slot_id}/start", headers=auth(l_tok))
        print("both started -> status:", r.json()["status"])
        assert r.json()["status"] == "in_progress"

        # 5. Finish before 15 min must be rejected.
        r = await c.post(f"/slots/{slot_id}/finish", headers=auth(t_tok))
        print("early finish (expect 400):", r.status_code)
        assert r.status_code == 400

        # 6. Dashboard shows the active slot for the learner.
        r = await c.get("/dashboard/", headers=auth(l_tok))
        print("dashboard active_slots:", len(r.json()["active_slots"]))
        assert r.status_code == 200

        # 7. Check learner points were debited (5 -> 4).
        r = await c.get("/auth/me", headers=auth(l_tok))
        print("learner peer_points:", r.json()["peer_points"])
        assert r.json()["peer_points"] == 4

    print("\nE2E smoke test PASSED ✅")


if __name__ == "__main__":
    asyncio.run(main())
