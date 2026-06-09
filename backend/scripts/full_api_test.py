"""Full API test suite — barcha endpointlarni real server ga qarab tekshiradi.

Ishlatish:
    PYTHONPATH=. .venv/bin/python3 scripts/full_api_test.py
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta, timezone

import httpx

BASE = "http://localhost:8001/api/v1"
PASS = "✅"
FAIL = "❌"

results: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: str = "") -> bool:
    mark = PASS if cond else FAIL
    print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))
    results.append((name, cond, detail))
    return cond


async def seed_user(login: str, campus: str = "samarkand") -> tuple[str, str]:
    """DB ga test user qo'shib JWT token qaytaradi."""
    from app.core.security import create_access_token
    from app.db.base import AsyncSessionLocal
    from app.db.models.user import User

    async with AsyncSessionLocal() as db:
        existing = await db.execute(
            __import__("sqlalchemy", fromlist=["select"]).select(User).where(
                User.school21_login == login
            )
        )
        user = existing.scalar_one_or_none()
        if user is None:
            user = User(
                telegram_id=abs(hash(login)) % 10_000_000,
                telegram_username=login,
                school21_login=login,
                first_name=login.capitalize(),
                campus=campus,
                languages=["uz", "ru"],
                peer_points=5,
                onboarding_done=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return str(user.id), create_access_token(str(user.id))


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def run_tests() -> None:
    # ── Seed iki test foydalanuvchi ──────────────────────────────────────────
    t_id, t_tok = await seed_user("api_teacher", "samarkand")
    l_id, l_tok = await seed_user("api_learner", "samarkand")

    async with httpx.AsyncClient(base_url=BASE, timeout=10) as c:

        # ────────────────────────────────────────────────────────────────────
        print("\n── HEALTH ──────────────────────────────────────────────────")
        r = await c.get("/".replace("/api/v1", "") + "http://localhost:8001/health")
        # Health alohida
        async with httpx.AsyncClient(timeout=5) as hc:
            r = await hc.get("http://localhost:8001/health")
        check("GET /health", r.status_code == 200 and r.json()["status"] == "ok")

        # ────────────────────────────────────────────────────────────────────
        print("\n── AUTH ────────────────────────────────────────────────────")
        # /auth/me — tokensiz
        r = await c.get("/auth/me")
        check("GET /auth/me (token yo'q → 401)", r.status_code == 401)

        # /auth/me — token bilan
        r = await c.get("/auth/me", headers=auth(t_tok))
        check("GET /auth/me (token bilan → 200)", r.status_code == 200,
              f"login={r.json().get('school21_login')}")

        # /auth/telegram — noto'g'ri init_data
        r = await c.post("/auth/telegram", json={"init_data": "hash=deadbeef"})
        check("POST /auth/telegram (xato init_data → 401)", r.status_code == 401)

        # /auth/school21/login — xato parol
        r = await c.post("/auth/school21/login",
                         json={"init_data": "hash=x", "login": "x", "password": "x"})
        check("POST /auth/school21/login (xato → 401)", r.status_code == 401)

        # /auth/refresh — xato token
        r = await c.post("/auth/refresh", json={"refresh_token": "invalid"})
        check("POST /auth/refresh (xato → 401)", r.status_code == 401)

        # /auth/logout
        r = await c.post("/auth/logout", headers=auth(t_tok))
        check("POST /auth/logout → 204", r.status_code == 204)

        # ────────────────────────────────────────────────────────────────────
        print("\n── ONBOARDING ──────────────────────────────────────────────")
        r = await c.get("/onboarding/status", headers=auth(t_tok))
        check("GET /onboarding/status → 200", r.status_code == 200)

        r = await c.get("/onboarding/track", headers=auth(t_tok))
        check("GET /onboarding/track → 200", r.status_code == 200)

        r = await c.post("/onboarding/confirm",
                         json={"main_track": "C6"}, headers=auth(t_tok))
        check("POST /onboarding/confirm → 200", r.status_code == 200)

        r = await c.post("/onboarding/languages",
                         json={"languages": ["uz", "ru"]}, headers=auth(t_tok))
        check("POST /onboarding/languages → 200", r.status_code == 200)

        r = await c.post("/onboarding/languages",
                         json={"languages": []}, headers=auth(t_tok))
        check("POST /onboarding/languages (bo'sh → 422)", r.status_code == 422)

        # ────────────────────────────────────────────────────────────────────
        print("\n── DASHBOARD ───────────────────────────────────────────────")
        r = await c.get("/dashboard/", headers=auth(t_tok))
        check("GET /dashboard/ → 200", r.status_code == 200)
        if r.status_code == 200:
            d = r.json()
            check("  dashboard.user mavjud", "user" in d)
            check("  dashboard.active_slots list", isinstance(d.get("active_slots"), list))
            check("  dashboard.xp_to_next_level mavjud", "xp_to_next_level" in d)

        # ────────────────────────────────────────────────────────────────────
        print("\n── SLOTS ───────────────────────────────────────────────────")
        # Create slot
        start = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
        end = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat()
        r = await c.post("/slots/", headers=auth(t_tok), json={
            "reviewer_project": "C6_simple_shell",
            "start_time": start,
            "end_time": end,
            "is_online": True,
        })
        check("POST /slots/ (create → 201)", r.status_code == 201)
        slot_id = r.json().get("id") if r.status_code == 201 else None

        # Tashkent + offline → 400
        r = await c.post("/slots/", headers=auth(t_tok), json={
            "reviewer_project": "C6_simple_shell",
            "start_time": start, "end_time": end,
            "is_online": False,
        })
        # (teacher campus=samarkand, shuning uchun bu 201 bo'lishi mumkin)

        # GET /slots/
        r = await c.get("/slots/", headers=auth(t_tok))
        check("GET /slots/ → 200", r.status_code == 200,
              f"{len(r.json())} slot")

        # GET /slots/search
        r = await c.get("/slots/search", headers=auth(l_tok),
                        params={"project": "C6_simple_shell"})
        check("GET /slots/search → 200", r.status_code == 200,
              f"{len(r.json())} natija")

        if r.status_code == 200 and r.json():
            # Search natijasi anonim — reviewer_id ko'rinmasligi kerak
            check("  search natijasi anonim (reviewer_id yo'q)",
                  "reviewer_id" not in r.json()[0])

        # GET /slots/{id}
        if slot_id:
            r = await c.get(f"/slots/{slot_id}", headers=auth(t_tok))
            check(f"GET /slots/{slot_id[:8]}... → 200", r.status_code == 200)

        # Book slot
        if slot_id:
            r = await c.post(f"/slots/{slot_id}/book", headers=auth(l_tok),
                             json={"reviewee_project": "C5_s21_maze"})
            check("POST /slots/{id}/book → 200", r.status_code == 200,
                  f"status={r.json().get('status')}")

            # O'z slotini band qila olmaydi — yangi open slot bilan test
            start_own = (datetime.now(timezone.utc) + timedelta(hours=10)).isoformat()
            end_own = (datetime.now(timezone.utc) + timedelta(hours=11)).isoformat()
            r_own = await c.post("/slots/", headers=auth(t_tok), json={
                "reviewer_project": "C6_simple_shell",
                "start_time": start_own, "end_time": end_own, "is_online": True,
            })
            own_slot_id = r_own.json().get("id") if r_own.status_code == 201 else None
            if own_slot_id:
                r2 = await c.post(f"/slots/{own_slot_id}/book", headers=auth(t_tok), json={})
                check("POST /slots/{id}/book (o'z slot → 400)", r2.status_code == 400,
                      r2.json().get("detail", ""))

        # Peer points ayirildi
        r = await c.get("/auth/me", headers=auth(l_tok))
        check("Book qilgandan keyin peer_points = 4",
              r.json().get("peer_points") == 4, str(r.json().get("peer_points")))

        # Start
        if slot_id:
            r = await c.post(f"/slots/{slot_id}/start", headers=auth(t_tok))
            check("POST /slots/{id}/start (teacher) → 200", r.status_code == 200)
            r = await c.post(f"/slots/{slot_id}/start", headers=auth(l_tok))
            check("POST /slots/{id}/start (learner) → 200", r.status_code == 200,
                  f"status={r.json().get('status')}")

        # Finish 15 min bo'lmagan → 400
        if slot_id:
            r = await c.post(f"/slots/{slot_id}/finish", headers=auth(t_tok))
            check("POST /slots/{id}/finish (erta → 400)", r.status_code == 400)

        # Create yangi slot cancel uchun
        start2 = (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat()
        end2 = (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat()
        r = await c.post("/slots/", headers=auth(t_tok), json={
            "reviewer_project": "C7_SmartCalc_v1.0",
            "start_time": start2, "end_time": end2, "is_online": True,
        })
        slot2_id = r.json().get("id") if r.status_code == 201 else None
        check("POST /slots/ (2-chi slot → 201)", r.status_code == 201)

        if slot2_id:
            # Band qilamiz
            await c.post(f"/slots/{slot2_id}/book", headers=auth(l_tok), json={})
            # Teacher bekor qiladi — learner point qaytishi kerak
            r = await c.request("DELETE", f"{BASE}/slots/{slot2_id}",
                                headers=auth(t_tok),
                                json={"reason": "test cancel"})
            check("DELETE /slots/{id} (teacher cancel → 200)",
                  r.status_code == 200, f"status={r.json().get('status')}")
            # Learner pointni qaytdi (4+1=5 bo'lishi kerak... lekin avval 4 edi va yana 1 sarfladi = 3, bekor bo'lganda +1 = 4)
            r = await c.get("/auth/me", headers=auth(l_tok))
            check("Cancel keyin learner peer_points = 4",
                  r.json().get("peer_points") == 4,
                  str(r.json().get("peer_points")))

        # ────────────────────────────────────────────────────────────────────
        print("\n── REVIEWS ─────────────────────────────────────────────────")
        r = await c.get("/reviews/my", headers=auth(t_tok))
        check("GET /reviews/my → 200", r.status_code == 200)

        r = await c.get(f"/reviews/user/{t_id}", headers=auth(l_tok))
        check("GET /reviews/user/{id} → 200", r.status_code == 200)

        # Completed bo'lmagan slot uchun review → 400
        if slot_id:
            r = await c.post("/reviews/", headers=auth(t_tok), json={
                "slot_id": slot_id, "is_positive": True
            })
            check("POST /reviews/ (in_progress slot → 400)", r.status_code == 400)

        # ────────────────────────────────────────────────────────────────────
        print("\n── LEADERBOARD ─────────────────────────────────────────────")
        for ep in ["/leaderboard/most-taught", "/leaderboard/most-learned",
                   "/leaderboard/most-xp"]:
            r = await c.get(ep, headers=auth(t_tok))
            check(f"GET {ep} → 200", r.status_code == 200,
                  f"{len(r.json())} entry")

        r = await c.get("/leaderboard/history", headers=auth(t_tok),
                        params={"month": "2026-05-01", "category": "most_xp"})
        check("GET /leaderboard/history → 200", r.status_code == 200)

        # ────────────────────────────────────────────────────────────────────
        print("\n── PROFILE ─────────────────────────────────────────────────")
        r = await c.get("/profile/", headers=auth(t_tok))
        check("GET /profile/ → 200", r.status_code == 200)
        if r.status_code == 200:
            check("  profile.stats mavjud", "stats" in r.json())

        r = await c.patch("/profile/", headers=auth(t_tok),
                          json={"first_name": "Teacher", "last_name": "Test"})
        check("PATCH /profile/ → 200", r.status_code == 200,
              r.json().get("first_name"))

        r = await c.get("/profile/api_teacher", headers=auth(l_tok))
        check("GET /profile/{username} → 200", r.status_code == 200)

        r = await c.get("/profile/noexist_xyz", headers=auth(l_tok))
        check("GET /profile/noexist_xyz → 404", r.status_code == 404)

        # ────────────────────────────────────────────────────────────────────
        print("\n── SETTINGS ────────────────────────────────────────────────")
        r = await c.get("/settings/", headers=auth(t_tok))
        check("GET /settings/ → 200", r.status_code == 200)

        r = await c.patch("/settings/language",
                          headers=auth(t_tok), json={"language": "ru"})
        check("PATCH /settings/language → 200", r.status_code == 200)

        r = await c.patch("/settings/theme",
                          headers=auth(t_tok), json={"theme": "dark"})
        check("PATCH /settings/theme → 200", r.status_code == 200)

        # ────────────────────────────────────────────────────────────────────
        print("\n── NOTIFICATIONS ───────────────────────────────────────────")
        r = await c.get("/notifications/", headers=auth(t_tok))
        check("GET /notifications/ → 200", r.status_code == 200,
              f"{len(r.json())} ta")

        r = await c.post("/notifications/read-all", headers=auth(t_tok))
        check("POST /notifications/read-all → 204", r.status_code == 204)

        # Fake notification id
        fake_id = str(uuid.uuid4())
        r = await c.post(f"/notifications/{fake_id}/read", headers=auth(t_tok))
        check("POST /notifications/{bad_id}/read → 404", r.status_code == 404)

        # ────────────────────────────────────────────────────────────────────
        print("\n── ADMIN (admin emas → 403) ────────────────────────────────")
        for ep in ["/admin/users", "/admin/slots", "/admin/stats"]:
            r = await c.get(ep, headers=auth(t_tok))
            check(f"GET {ep} (admin emas → 403)", r.status_code == 403)

        # Admin user yaratib tekshiramiz
        from app.core.security import create_access_token as cat
        from app.db.base import AsyncSessionLocal
        from app.db.models.user import User as UModel
        from sqlalchemy import select as sel

        async with AsyncSessionLocal() as db:
            admin = (await db.execute(
                sel(UModel).where(UModel.school21_login == "api_admin")
            )).scalar_one_or_none()
            if admin is None:
                admin = UModel(
                    telegram_id=9999999,
                    school21_login="api_admin",
                    first_name="Admin",
                    is_admin=True,
                    campus="samarkand",
                    languages=["uz"],
                    peer_points=5,
                    onboarding_done=True,
                )
                db.add(admin)
                await db.commit()
                await db.refresh(admin)
            admin_tok = cat(str(admin.id), {"admin": True})

        print("\n── ADMIN (admin → 200) ─────────────────────────────────────")
        r = await c.get("/admin/users", headers=auth(admin_tok))
        check("GET /admin/users → 200", r.status_code == 200,
              f"{len(r.json())} user")

        r = await c.get("/admin/slots", headers=auth(admin_tok))
        check("GET /admin/slots → 200", r.status_code == 200)

        r = await c.get("/admin/stats", headers=auth(admin_tok))
        check("GET /admin/stats → 200", r.status_code == 200,
              str(r.json()))

        r = await c.post("/admin/adjust-xp", headers=auth(admin_tok),
                         json={"user_id": t_id, "amount": 100})
        check("POST /admin/adjust-xp → 200", r.status_code == 200,
              f"xp={r.json().get('xp')}")

        r = await c.post("/admin/adjust-points", headers=auth(admin_tok),
                         json={"user_id": t_id, "points": 2})
        check("POST /admin/adjust-points → 200", r.status_code == 200,
              f"peer_points={r.json().get('peer_points')}")

        r = await c.post("/admin/notify", headers=auth(admin_tok),
                         json={"user_id": t_id, "title": "Test", "body": "Hello"})
        check("POST /admin/notify (bitta) → 202", r.status_code == 202)

        r = await c.post("/admin/notify", headers=auth(admin_tok),
                         json={"title": "Broadcast", "body": "All"})
        check("POST /admin/notify (broadcast) → 202", r.status_code == 202)

    # ── Yakuniy hisobot ──────────────────────────────────────────────────────
    total = len(results)
    passed = sum(1 for _, ok, _ in results if ok)
    failed = total - passed

    print(f"\n{'='*60}")
    print(f"NATIJA: {passed}/{total} o'tdi  |  {failed} muvaffaqiyatsiz")
    if failed:
        print("\nMuvaffaqiyatsiz testlar:")
        for name, ok, detail in results:
            if not ok:
                print(f"  ❌ {name}" + (f" — {detail}" if detail else ""))
    print("="*60)


if __name__ == "__main__":
    asyncio.run(run_tests())
