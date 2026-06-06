"""Session (sessiya) modeli."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..base import Base
from ..types import GUID
from .enums import SessionStatus

if TYPE_CHECKING:
    from .review import Review
    from .slot import Slot


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    slot_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("slots.id"))
    mentor_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    mentee_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    chat_group_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finish_requested_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    mentor_comment: Mapped[str | None] = mapped_column(Text)
    mentee_comment: Mapped[str | None] = mapped_column(Text)
    mentor_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    mentee_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    mentor_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mentee_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    coins_transferred: Mapped[bool] = mapped_column(Boolean, default=False)
    xp_awarded: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(32), default=SessionStatus.ACTIVE.value)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    slot: Mapped[Slot] = relationship("Slot", back_populates="session")
    reviews: Mapped[list[Review]] = relationship("Review", back_populates="session")

    def __repr__(self) -> str:
        return f"<Session id={self.id} status={self.status}>"
