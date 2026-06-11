"""User-related DB operations for bot admin."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, or_, select

from app.db.base import AsyncSessionLocal
from app.db.models.slot import Slot, SlotStatus
from app.db.models.user import User
from app.services.points_service import add_peer_points
from app.services.xp_service import apply_xp

_TEST_LOGINS = {"api_admin", "api_teacher", "api_learner"}


async def search_users(query: str, limit: int = 10) -> list[User]:
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(
            or_(
                User.school21_login.ilike(f"%{query}%"),
                User.telegram_username.ilike(f"%{query}%"),
            ),
            User.school21_login.notin_(_TEST_LOGINS),
        ).limit(limit)
        return list((await db.execute(stmt)).scalars().all())


async def get_user_by_login(login: str) -> User | None:
    async with AsyncSessionLocal() as db:
        return (await db.execute(
            select(User).where(User.school21_login == login)
        )).scalar_one_or_none()


async def get_recent_users(limit: int = 5) -> list[User]:
    async with AsyncSessionLocal() as db:
        stmt = (
            select(User).where(User.school21_login.notin_(_TEST_LOGINS))
            .order_by(User.created_at.desc()).limit(limit)
        )
        return list((await db.execute(stmt)).scalars().all())


async def get_user_stats_summary() -> dict:
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
    async with AsyncSessionLocal() as db:
        total = (await db.execute(select(func.count(User.id)).where(
            User.school21_login.notin_(_TEST_LOGINS)))).scalar_one()
        active = (await db.execute(select(func.count(User.id)).where(
            User.is_active.is_(True), User.school21_login.notin_(_TEST_LOGINS)))).scalar_one()
        blocked = (await db.execute(select(func.count(User.id)).where(
            User.is_active.is_(False), User.school21_login.notin_(_TEST_LOGINS)))).scalar_one()
        new_today = (await db.execute(select(func.count(User.id)).where(
            User.created_at >= today, User.school21_login.notin_(_TEST_LOGINS)))).scalar_one()
        logged_in = (await db.execute(select(func.count(User.id)).where(
            User.is_logged_in.is_(True), User.school21_login.notin_(_TEST_LOGINS)))).scalar_one()
    return {"total": total, "active": active, "blocked": blocked,
            "new_today": new_today, "logged_in": logged_in}


async def toggle_user_admin(login: str) -> bool | None:
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.school21_login == login))).scalar_one_or_none()
        if not user:
            return None
        user.is_admin = not user.is_admin
        await db.commit()
        return user.is_admin


async def toggle_user_block(login: str) -> bool | None:
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.school21_login == login))).scalar_one_or_none()
        if not user:
            return None
        user.is_active = not user.is_active
        await db.commit()
        return user.is_active


async def adjust_user_xp(login: str, amount: int) -> int | None:
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.school21_login == login))).scalar_one_or_none()
        if not user:
            return None
        await apply_xp(db, user, amount, "admin_adjust")
        await db.commit()
        return user.xp


async def adjust_user_points(login: str, amount: int) -> int | None:
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.school21_login == login))).scalar_one_or_none()
        if not user:
            return None
        add_peer_points(user, amount)
        await db.commit()
        return user.peer_points


async def force_logout(login: str) -> bool:
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.school21_login == login))).scalar_one_or_none()
        if not user:
            return False
        user.is_logged_in = False
        await db.commit()
        return True


async def unlink_telegram(login: str) -> bool:
    """Admin: foydalanuvchining telegram bog'lanishini uzish."""
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.school21_login == login))).scalar_one_or_none()
        if not user:
            return False
        user.telegram_id = None
        user.telegram_username = None
        user.is_logged_in = False
        await db.commit()
        return True


async def get_platform_stats() -> dict:
    async with AsyncSessionLocal() as db:
        total = (await db.execute(select(func.count(User.id)).where(
            User.school21_login.notin_(_TEST_LOGINS)))).scalar_one()
        active = (await db.execute(select(func.count(User.id)).where(
            User.is_active.is_(True), User.school21_login.notin_(_TEST_LOGINS)))).scalar_one()
        logged_in = (await db.execute(select(func.count(User.id)).where(
            User.is_logged_in.is_(True), User.school21_login.notin_(_TEST_LOGINS)))).scalar_one()
        admins = (await db.execute(select(func.count(User.id)).where(
            User.is_admin.is_(True), User.school21_login.notin_(_TEST_LOGINS)))).scalar_one()
        slots_total = (await db.execute(select(func.count(Slot.id)))).scalar_one()
        slots_open = (await db.execute(select(func.count(Slot.id)).where(
            Slot.status == SlotStatus.OPEN.value))).scalar_one()
        slots_booked = (await db.execute(select(func.count(Slot.id)).where(
            Slot.status == SlotStatus.BOOKED.value))).scalar_one()
        slots_done = (await db.execute(select(func.count(Slot.id)).where(
            Slot.status == SlotStatus.COMPLETED.value))).scalar_one()
        avg_dur = (await db.execute(select(func.avg(Slot.duration_minutes)).where(
            Slot.duration_minutes.isnot(None)))).scalar_one()
    return {"users": total, "active": active, "logged_in": logged_in,
            "admins": admins, "slots": slots_total, "open": slots_open,
            "booked": slots_booked, "completed": slots_done,
            "avg_minutes": round(float(avg_dur), 1) if avg_dur else 0}


async def get_user_ids_by_target(target: str) -> list[int]:
    async with AsyncSessionLocal() as db:
        stmt = select(User.telegram_id).where(User.telegram_id.isnot(None))
        if target == "active":
            stmt = stmt.where(User.is_active.is_(True), User.is_logged_in.is_(True))
        elif target == "tashkent":
            stmt = stmt.where(User.campus.ilike("%tashkent%"), User.is_active.is_(True))
        elif target == "samarkand":
            stmt = stmt.where(User.campus.ilike("%samarkand%"), User.is_active.is_(True))
        elif target == "admins":
            stmt = stmt.where(User.is_admin.is_(True))
        else:
            stmt = stmt.where(User.is_active.is_(True))
        return [r for r in (await db.execute(stmt)).scalars().all() if r]
