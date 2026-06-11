"""User model."""
from __future__ import annotations

import uuid

from sqlalchemy import BigInteger, Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger, unique=True, nullable=True, index=True
    )
    telegram_username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    school21_login: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    school21_token_enc: Mapped[str | None] = mapped_column(Text, nullable=True)

    first_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    campus: Mapped[str | None] = mapped_column(String(64), nullable=True)
    current_location: Mapped[str | None] = mapped_column(String(256), nullable=True)
    core_program: Mapped[str | None] = mapped_column(String(128), nullable=True)
    main_track: Mapped[str | None] = mapped_column(String(128), nullable=True)
    email: Mapped[str | None] = mapped_column(String(256), nullable=True)
    coalition_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    xp: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    peer_points: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    peer_coins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    languages: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    onboarding_done: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_logged_in: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
