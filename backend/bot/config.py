"""Ilova konfiguratsiyasi (Pydantic Settings orqali .env dan o'qiladi)."""

from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Markaziy sozlamalar. Majburiy maydonlar yetishmasa ishga tushishda xato beradi."""

    # Bot
    BOT_TOKEN: str
    WEBHOOK_URL: str = ""
    WEBHOOK_PATH: str = "/webhook"
    SECRET_KEY: str

    # Database / Redis
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    # School 21 (Keycloak + REST)
    S21_TOKEN_URL: str = (
        "https://auth.21-school.ru/auth/realms/EduPowerKeycloak/protocol/openid-connect/token"
    )
    S21_API_URL: str = "https://platform.21-school.ru/services/21-school/api/v1"
    S21_CLIENT_ID: str = "s21-open-api"

    # App constants
    DEBUG: bool = False
    SQL_ECHO: bool = False
    DEFAULT_COINS: int = 5
    MAX_COINS: int = 15
    REMINDER_MINUTES: int = 15
    XP_PER_SESSION: int = 50
    COIN_PER_SESSION: int = 1
    SESSION_DEFAULT_MINUTES: int = 60
    MAX_SESSION_HOURS: int = 4
    TIMEZONE_OFFSET_HOURS: int = 5  # O'zbekiston (UTC+5)

    # Chat backend: "relay" | "userbot"
    CHAT_BACKEND: str = "relay"

    # API / Mini App (JWT)
    JWT_SECRET: str = ""  # bo'sh bo'lsa SECRET_KEY ishlatiladi
    JWT_EXPIRE_HOURS: int = 24
    API_CORS_ORIGINS: str = "*"  # vergul bilan ajratilgan ro'yxat yoki "*"

    # Admin
    ADMIN_IDS: list[int] = []

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def _parse_admin_ids(cls, value: object) -> object:
        """ADMIN_IDS ni "1,2,3" satr yoki bitta son ko'rinishidan ham qabul qilish."""
        if value is None or value == "":
            return []
        if isinstance(value, int):
            return [value]
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            return [int(part) for part in value.split(",") if part.strip()]
        return value

    @field_validator("CHAT_BACKEND")
    @classmethod
    def _validate_chat_backend(cls, value: str) -> str:
        allowed = {"relay", "userbot"}
        if value not in allowed:
            raise ValueError(f"CHAT_BACKEND must be one of {allowed}, got {value!r}")
        return value

    @field_validator("API_CORS_ORIGINS", mode="before")
    @classmethod
    def _normalize_cors(cls, value: object) -> object:
        # Faqat satr sifatida saqlaymiz; ro'yxatga property orqali aylantiramiz
        if isinstance(value, (list, tuple)):
            return ",".join(str(v) for v in value)
        return value

    @property
    def cors_origins(self) -> list[str]:
        raw = (self.API_CORS_ORIGINS or "*").strip()
        if not raw or raw == "*":
            return ["*"]
        return [part.strip() for part in raw.split(",") if part.strip()]

    @property
    def jwt_secret(self) -> str:
        return self.JWT_SECRET or self.SECRET_KEY


def get_settings() -> Settings:
    """Settings instansiyasini yaratish (test/lazy yuklash uchun qulay)."""
    return Settings()  # type: ignore[call-arg]


@lru_cache(maxsize=1)
def _cached_settings() -> Settings:
    return get_settings()


def __getattr__(name: str) -> object:
    """Modul darajasida lazy `settings` taqdim etish.

    `from bot.config import settings` ishlaydi, lekin Settings faqat birinchi
    murojaatda yaratiladi (import vaqtida .env majburiy emas).
    """
    if name == "settings":
        return _cached_settings()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
