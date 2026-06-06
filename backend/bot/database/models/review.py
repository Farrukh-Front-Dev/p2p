"""Review (baholash) modeli."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..base import Base
from ..types import GUID

if TYPE_CHECKING:
    from .session import Session


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating_range"),)

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("sessions.id"))
    reviewer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    reviewed_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    session: Mapped[Session] = relationship("Session", back_populates="reviews")

    def __repr__(self) -> str:
        return f"<Review session={self.session_id} role={self.role} rating={self.rating}>"
