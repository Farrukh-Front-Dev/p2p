"""Transaction (tanga tranzaksiyasi) modeli."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..base import Base
from ..types import GUID

if TYPE_CHECKING:
    from .user import User


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String(32))
    slot_id: Mapped[uuid.UUID | None] = mapped_column(GUID, ForeignKey("slots.id"), nullable=True)
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID, ForeignKey("sessions.id"), nullable=True
    )
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped[User] = relationship("User", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction user={self.user_id} amount={self.amount} type={self.type}>"
