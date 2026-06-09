"""Notification schemas."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str
    title: str | None = None
    body: str | None = None
    slot_id: uuid.UUID | None = None
    is_read: bool
    created_at: datetime
