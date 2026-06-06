"""User modeli."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..base import Base
from ..types import StringArray

if TYPE_CHECKING:
    from .slot import Slot
    from .transaction import Transaction


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram ID
    username: Mapped[str | None] = mapped_column(String(64))
    school21_login: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    nickname: Mapped[str | None] = mapped_column(String(64))
    avatar_url: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(8), default="uz")
    directions: Mapped[list[str]] = mapped_column(StringArray, default=list)
    coins: Mapped[int] = mapped_column(Integer, default=5)
    max_coins: Mapped[int] = mapped_column(Integer, default=15)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    total_taught: Mapped[int] = mapped_column(Integer, default=0)
    total_learned: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    mentor_slots: Mapped[list[Slot]] = relationship(
        "Slot",
        foreign_keys="Slot.mentor_id",
        back_populates="mentor",
    )
    mentee_slots: Mapped[list[Slot]] = relationship(
        "Slot",
        foreign_keys="Slot.mentee_id",
        back_populates="mentee",
    )
    transactions: Mapped[list[Transaction]] = relationship(
        "Transaction",
        back_populates="user",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} login={self.school21_login!r} coins={self.coins}>"
