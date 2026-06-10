"""Bot settings — app.core.config dan mustaqil."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    TELEGRAM_REQUIRED_CHANNEL: str = ""

    # Backend API URL (bot shu orqali API ga murojaat qiladi)
    API_BASE_URL: str = "http://localhost:8000"

    # DB (bot to'g'ridan-to'g'ri DB ga kirishi kerak bo'lsa)
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/p2p_db"


@lru_cache
def get_settings() -> BotSettings:
    return BotSettings()


settings = get_settings()
