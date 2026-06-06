"""Konfiguratsiya moduli testlari."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from bot.config import Settings


def _base_env() -> dict[str, str]:
    return {
        "BOT_TOKEN": "abc:123",
        "SECRET_KEY": "s3cr3t",
        "DATABASE_URL": "postgresql+asyncpg://u:p@localhost/db",
    }


def test_defaults_are_applied():
    s = Settings(_env_file=None, **_base_env())  # type: ignore[arg-type]
    assert s.DEFAULT_COINS == 5
    assert s.MAX_COINS == 15
    assert s.REMINDER_MINUTES == 15
    assert s.XP_PER_SESSION == 50
    assert s.COIN_PER_SESSION == 1
    assert s.CHAT_BACKEND == "relay"
    assert s.S21_CLIENT_ID == "s21-open-api"
    assert s.ADMIN_IDS == []


def test_missing_required_field_raises(monkeypatch):
    # Muhitdagi majburiy o'zgaruvchilarni olib tashlash (conftest ularni o'rnatadi)
    for key in ("BOT_TOKEN", "SECRET_KEY", "DATABASE_URL"):
        monkeypatch.delenv(key, raising=False)
    env = _base_env()
    del env["BOT_TOKEN"]
    # _env_file=None: .env faylini o'qimaslik, sof validatsiya uchun
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **env)  # type: ignore[arg-type]


def test_admin_ids_parsed_from_csv_string():
    s = Settings(ADMIN_IDS="111, 222 ,333", **_base_env())  # type: ignore[arg-type]
    assert s.ADMIN_IDS == [111, 222, 333]


def test_admin_ids_empty_string():
    s = Settings(ADMIN_IDS="", **_base_env())  # type: ignore[arg-type]
    assert s.ADMIN_IDS == []


def test_invalid_chat_backend_raises():
    with pytest.raises(ValidationError):
        Settings(CHAT_BACKEND="carrier-pigeon", **_base_env())  # type: ignore[arg-type]
