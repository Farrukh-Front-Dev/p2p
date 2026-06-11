"""Senior-level full integration test — barcha API, business logic, xavfsizlik.

Ishlatish:
    PYTHONPATH=. .venv/bin/python scripts/full_test.py
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta, timezone

import httpx

BASE = "http://localhost:8001/api/v1"
results: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: str = "") -> bool:
    mark = "✅" if cond else "❌"
    print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))
    results.append((name, cond, detail))
    return cond


async def seed_user(login: str, campus: str = "samarkand", tg_id: int | None = None):
    from app.core.security import create_access_token
    from app.db.base import AsyncSessionLocal
    from app.db.models.user import User
    from sqlalchemy import select
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.school21_login == login))).scalar_one_or_none()
        if user is None:
            user = User(
                telegram_id=tg_id or abs(hash(login)) % 10_000_000,
                telegram_username=login,
                school21_login=login,
                first_name=login.capitalize(),
                campus=campus,
                languages=["uz", "ru"],
                peer_points=5,
                onboarding_done=True,
                is_logged_in=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
    return str(user.id), create_access_token(str(user.id))


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def run():
    t_id, t_tok = await seed_user("t_teacher", "samarkand")
    l_id, l_tok = await seed_user("t_learner", "samarkand")

    async with httpx.AsyncClient(base_url=BASE, timeout=15) as c:

        # ═══════════════════════════════════════════════════════════════════════
        print("\n═══ 1. AUTH ═══════════════════════════════════════════════════")
        # ═══════════════════════════════════════════════════════════════════════

        r = await c.get("/auth/me")
        check("GET /me tokensiz → 401", r.status_code == 401)

        r = await c.get("/auth/me", headers=auth(t_tok))
        check("GET /me token bilan → 200", r.status_code == 200, r.json().get("school21_login"))

        r = await c.post("/auth/login", json={"login": "x", "password": "x"})
        check("POST /login xato creds → 401", r.status_code == 401)

        r = await c.post("/auth/verify-code", json={"temp_token": "invalid", "code": "000000"})
        check("POST /verify-code xato token → 400", r.status_code == 400)

        r = await c.post("/auth/refresh", json={"refresh_token": "bad"})
        check("POST /refresh xato → 401", r.status_code == 401)

        r = await c.post("/auth/logout", headers=auth(t_tok))
        check("POST /logout → 204", r.status_code == 204)

        # Re-login (is_logged_in ni qayta True qilish)
        from app.db.base import AsyncSessionLocal
        from app.db.models.user import User
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            u = (await db.execute(select(User).where(User.school21_login == "t_teacher"))).scalar_one()
            u.is_logged_in = True
            await db.commit()

        # ═══════════════════════════════════════════════════════════════════════
        print("\n═══ 2. ONBOARDING ═════════════════════════════════════════════")
        # ═══════════════════════════════════════════════════════════════════════

        r = await c.get("/onboarding/status", headers=auth(t_tok))
        check("GET /onboarding/status → 200", r.status_code == 200)

        r = await c.post("/onboarding/confirm", json={"main_track": "DSB"}, headers=auth(t_tok))
        check("POST /onboarding/confirm → 200", r.status_code == 200)

        r = await c.post("/onboarding/languages", json={"languages": ["uz", "en"]}, headers=auth(t_tok))
        check("POST /onboarding/languages → 200", r.status_code == 200)

        r = await c.post("/onboarding/languages", json={"languages": []}, headers=auth(t_tok))
        check("POST /onboarding/languages bo'sh → 422", r.status_code == 422)

        # ═══════════════════════════════════════════════════════════════════════
        print("\n═══ 3. DASHBOARD ══════════════════════════════════════════════")
        # ═══════════════════════════════════════════════════════════════════════

        r = await c.get("/dashboard/", headers=auth(t_tok))
        check("GET /dashboard → 200", r.status_code == 200)
        if r.status_code == 200:
            d = r.json()
            check("  user mavjud", "user" in d)
            check("  active_slots list", isinstance(d.get("active_slots"), list))

        # ═══════════════════════════════════════════════════════════════════════
        print("\n═══ 4. SLOTS LIFECYCLE ════════════════════════════════════════")
        # ═══════════════════════════════════════════════════════════════════════

        start = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
        end = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat()

        r = await c.post("/slots/", headers=auth(t_tok), json={
            "reviewer_project": "DSB1_intro", "start_time": start, "end_time": end, "is_online": True,
        })
        check("POST /slots create → 201", r.status_code == 201)
        slot_id = r.json()["id"] if r.status_code == 201 else None

        r = await c.get("/slots/", headers=auth(t_tok))
        check("GET /slots list → 200", r.status_code == 200)

        r = await c.get("/slots/search", headers=auth(l_tok), params={"project": "DSB1_intro"})
        check("GET /slots/search → 200", r.status_code == 200)
        if r.status_code == 200 and r.json():
            check("  anonim (reviewer_id yo'q)", "reviewer_id" not in r.json()[0])

        if slot_id:
            r = await c.get(f"/slots/{slot_id}", headers=auth(t_tok))
            check("GET /slots/{id} → 200", r.status_code == 200)

            # O'z slotini book qila olmaydi
            r = await c.post(f"/slots/{slot_id}/book", headers=auth(t_tok), json={})
            check("Book o'z slot → 400", r.status_code == 400)

            # Learner book qiladi
            r = await c.post(f"/slots/{slot_id}/book", headers=auth(l_tok), json={"reviewee_project": "DSB1_intro"})
            check("POST /book → 200 booked", r.status_code == 200 and r.json().get("status") == "booked")

            # Peer points tekshiruv
            r = await c.get("/auth/me", headers=auth(l_tok))
            check("Learner points = 4", r.json().get("peer_points") == 4)

            # Start
            await c.post(f"/slots/{slot_id}/start", headers=auth(t_tok))
            r = await c.post(f"/slots/{slot_id}/start", headers=auth(l_tok))
            check("Both start → in_progress", r.json().get("status") == "in_progress")

            # Early finish → 400
            r = await c.post(f"/slots/{slot_id}/finish", headers=auth(t_tok))
            check("Early finish → 400", r.status_code == 400)

        # Cancel test
        start2 = (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat()
        end2 = (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat()
        r = await c.post("/slots/", headers=auth(t_tok), json={
            "reviewer_project": "C3_s21", "start_time": start2, "end_time": end2, "is_online": True,
        })
        sid2 = r.json()["id"] if r.status_code == 201 else None
        if sid2:
            await c.post(f"/slots/{sid2}/book", headers=auth(l_tok), json={})
            r = await c.request("DELETE", f"{BASE}/slots/{sid2}", headers=auth(t_tok), json={"reason": "test"})
            check("DELETE cancel → 200 cancelled", r.status_code == 200 and r.json().get("status") == "cancelled")

        # ═══════════════════════════════════════════════════════════════════════
        print("\n═══ 5. REVIEWS ════════════════════════════════════════════════")
        # ═══════════════════════════════════════════════════════════════════════

        r = await c.get("/reviews/my", headers=auth(t_tok))
        check("GET /reviews/my → 200", r.status_code == 200)

        if slot_id:
            r = await c.post("/reviews/", headers=auth(t_tok), json={"slot_id": slot_id, "is_positive": True})
            check("POST review in_progress slot → 400", r.status_code == 400)

        # ═══════════════════════════════════════════════════════════════════════
        print("\n═══ 6. LEADERBOARD ════════════════════════════════════════════")
        # ═══════════════════════════════════════════════════════════════════════

        for ep in ["/leaderboard/most-taught", "/leaderboard/most-learned", "/leaderboard/most-xp"]:
            r = await c.get(ep, headers=auth(t_tok))
            check(f"GET {ep} → 200", r.status_code == 200)

        r = await c.get("/leaderboard/history", headers=auth(t_tok), params={"month": "2026-05-01", "category": "most_xp"})
        check("GET /leaderboard/history → 200", r.status_code == 200)

        # ═══════════════════════════════════════════════════════════════════════
        print("\n═══ 7. PROFILE ════════════════════════════════════════════════")
        # ═══════════════════════════════════════════════════════════════════════

        r = await c.get("/profile/", headers=auth(t_tok))
        check("GET /profile → 200 + stats", r.status_code == 200 and "stats" in r.json())

        r = await c.patch("/profile/", headers=auth(t_tok), json={"first_name": "Senior"})
        check("PATCH /profile → 200", r.status_code == 200)

        r = await c.get("/profile/t_teacher", headers=auth(l_tok))
        check("GET /profile/{username} → 200", r.status_code == 200)

        r = await c.get("/profile/nonexist_xyz", headers=auth(l_tok))
        check("GET /profile/nonexist → 404", r.status_code == 404)

        # ═══════════════════════════════════════════════════════════════════════
        print("\n═══ 8. SETTINGS ═══════════════════════════════════════════════")
        # ═══════════════════════════════════════════════════════════════════════

        r = await c.get("/settings/", headers=auth(t_tok))
        check("GET /settings → 200", r.status_code == 200)

        r = await c.patch("/settings/language", headers=auth(t_tok), json={"language": "en"})
        check("PATCH /settings/language → 200", r.status_code == 200)

        r = await c.patch("/settings/theme", headers=auth(t_tok), json={"theme": "dark"})
        check("PATCH /settings/theme → 200", r.status_code == 200)

        # ═══════════════════════════════════════════════════════════════════════
        print("\n═══ 9. NOTIFICATIONS ══════════════════════════════════════════")
        # ═══════════════════════════════════════════════════════════════════════

        r = await c.get("/notifications/", headers=auth(t_tok))
        check("GET /notifications → 200", r.status_code == 200)

        r = await c.post("/notifications/read-all", headers=auth(t_tok))
        check("POST /notifications/read-all → 204", r.status_code == 204)

        fake = str(uuid.uuid4())
        r = await c.post(f"/notifications/{fake}/read", headers=auth(t_tok))
        check("POST /notifications/bad_id → 404", r.status_code == 404)

        # ═══════════════════════════════════════════════════════════════════════
        print("\n═══ 10. ADMIN GUARD ═══════════════════════════════════════════")
        # ═══════════════════════════════════════════════════════════════════════

        r = await c.get("/admin/users", headers=auth(t_tok))
        check("GET /admin/users (no admin) → 403", r.status_code == 403)

        from app.core.security import create_access_token
        async with AsyncSessionLocal() as db:
            admin = (await db.execute(select(User).where(User.school21_login == "t_admin"))).scalar_one_or_none()
            if not admin:
                admin = User(telegram_id=9999998, school21_login="t_admin", is_admin=True,
                             campus="samarkand", languages=["uz"], peer_points=5, is_logged_in=True)
                db.add(admin)
                await db.commit()
                await db.refresh(admin)
        admin_tok = create_access_token(str(admin.id), {"admin": True})

        r = await c.get("/admin/users", headers=auth(admin_tok))
        check("GET /admin/users (admin) → 200", r.status_code == 200)

        r = await c.get("/admin/stats", headers=auth(admin_tok))
        check("GET /admin/stats → 200", r.status_code == 200)

        r = await c.post("/admin/adjust-xp", headers=auth(admin_tok), json={"user_id": t_id, "amount": 100})
        check("POST /admin/adjust-xp → 200", r.status_code == 200, f"xp={r.json().get('xp')}")

        r = await c.post("/admin/notify", headers=auth(admin_tok), json={"user_id": t_id, "title": "Test", "body": "OK"})
        check("POST /admin/notify → 202", r.status_code == 202)

        # ═══════════════════════════════════════════════════════════════════════
        print("\n═══ 11. XAVFSIZLIK ════════════════════════════════════════════")
        # ═══════════════════════════════════════════════════════════════════════

        # Admin panel himoyasi
        async with httpx.AsyncClient(timeout=5) as hc:
            r = await hc.get("http://localhost:8001/admin/")
            check("SQLAdmin → 302 (login kerak)", r.status_code == 302)

        # CORS
        async with httpx.AsyncClient(timeout=5) as hc:
            r = await hc.options(
                "http://localhost:8001/api/v1/auth/me",
                headers={"Origin": "http://evil.com", "Access-Control-Request-Method": "GET"},
            )
            origin = r.headers.get("access-control-allow-origin", "")
            check("CORS evil.com bloklangan", "evil.com" not in origin)

            r = await hc.options(
                "http://localhost:8001/api/v1/auth/me",
                headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
            )
            origin = r.headers.get("access-control-allow-origin", "")
            check("CORS localhost:3000 OK", "localhost:3000" in origin)

        # Rate limit (login endpoint ga 6+ so'rov)
        codes = []
        for i in range(7):
            r = await c.post("/auth/login", json={"login": "x", "password": "x"})
            codes.append(r.status_code)
        check("Rate limit ishlaydi (429)", 429 in codes, str(codes))

    # ═══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    total = len(results)
    passed = sum(1 for _, ok, _ in results if ok)
    failed = total - passed
    print(f"NATIJA: {passed}/{total} o'tdi  |  {failed} muvaffaqiyatsiz")
    if failed:
        print("\nMuvaffaqiyatsiz:")
        for name, ok, detail in results:
            if not ok:
                print(f"  ❌ {name}" + (f" — {detail}" if detail else ""))
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run())
