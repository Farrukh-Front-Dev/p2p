"""BotSettings — singleton dynamic bot configuration."""
from __future__ import annotations

from sqlalchemy import Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class BotSettings(Base, TimestampMixin):
    __tablename__ = "bot_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    subscription_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    webapp_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    maintenance_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    maintenance_message: Mapped[str | None] = mapped_column(
        Text, default="🔧 Bot texnik ishlar uchun vaqtincha to'xtatilgan."
    )
