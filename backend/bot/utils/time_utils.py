"""Vaqt formatlash yordamchilari."""

from __future__ import annotations

from datetime import datetime, timedelta


def now_local() -> datetime:
    """Joriy mahalliy vaqt (sozlamalardagi TIMEZONE_OFFSET_HOURS bo'yicha).

    Naive datetime qaytaradi (DB ham naive saqlaydi). Butun tizim bir xil
    mahalliy vaqtdan foydalanadi, shuning uchun solishtirishlar izchil bo'ladi.
    """
    from ..config import settings

    return datetime.utcnow() + timedelta(hours=settings.TIMEZONE_OFFSET_HOURS)


def fmt_time(dt: datetime) -> str:
    """HH:MM ko'rinishida."""
    return dt.strftime("%H:%M")


def fmt_datetime(dt: datetime) -> str:
    """DD.MM HH:MM ko'rinishida."""
    return dt.strftime("%d.%m %H:%M")


def fmt_range(start: datetime, end: datetime) -> str:
    """DD.MM HH:MM - HH:MM ko'rinishida."""
    return f"{fmt_datetime(start)} - {fmt_time(end)}"
