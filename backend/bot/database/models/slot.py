"""Slot modeli."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..base import Base
from ..types import GUID
from .enums import SlotStatus

if TYPE_CHECKING:
    from .session import Session
    from .user import User


class Slot(Base):
    __tablename__ = "slots"
    __table_args__ = (
        Index("idx_slots_status", "status"),
        Index("idx_slots_direction", "direction"),
        Index("idx_slots_start_time", "start_time"),
        Index("idx_slots_mentor_id", "mentor_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    mentor_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    mentee_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    direction: Mapped[str] = mapped_column(String(64))
    title: Mapped[str | None] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(Text)
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(32), default=SlotStatus.OPEN.value)
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reveal_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    chat_group_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    mentor: Mapped[User] = relationship(
        "User", foreign_keys=[mentor_id], back_populates="mentor_slots"
    )
    mentee: Mapped[User | None] = relationship(
        "User", foreign_keys=[mentee_id], back_populates="mentee_slots"
    )
    session: Mapped[Session | None] = relationship("Session", back_populates="slot", uselist=False)

    def __repr__(self) -> str:
        return f"<Slot id={self.id} dir={self.direction!r} status={self.status}>"
