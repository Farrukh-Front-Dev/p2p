"""Slot model."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.user import User


class SlotStatus(str, enum.Enum):
    OPEN = "open"
    BOOKED = "booked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ABSENT = "absent"


class Slot(Base, TimestampMixin):
    __tablename__ = "slots"
    __table_args__ = (
        Index("ix_slots_match", "status", "reviewer_project", "campus"),
        Index("ix_slots_reviewer_id", "reviewer_id"),
        Index("ix_slots_reviewee_id", "reviewee_id"),
        Index("ix_slots_start_time", "start_time"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    reviewee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    reviewer_project: Mapped[str] = mapped_column(String(128), nullable=False)
    reviewee_project: Mapped[str | None] = mapped_column(String(128), nullable=True)

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    actual_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    actual_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    status: Mapped[str] = mapped_column(
        String(20), default=SlotStatus.OPEN.value, nullable=False
    )
    is_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    campus: Mapped[str] = mapped_column(String(64), nullable=False)

    reviewer_started: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewee_started: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewer_finished: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewee_finished: Mapped[bool] = mapped_column(Boolean, default=False)

    absent_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    absent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    cancel_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    reviewer: Mapped["User"] = relationship(
        "User", foreign_keys=[reviewer_id], lazy="selectin"
    )
    reviewee: Mapped["User | None"] = relationship(
        "User", foreign_keys=[reviewee_id], lazy="selectin"
    )
