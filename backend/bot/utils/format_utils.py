"""Formatlash yordamchilari."""

from __future__ import annotations


def display_name(user) -> str:
    """Foydalanuvchining ko'rsatiladigan nomi (@username yoki nickname)."""
    if user is None:
        return "?"
    if getattr(user, "username", None):
        return f"@{user.username}"
    return getattr(user, "nickname", None) or getattr(user, "school21_login", "?")
