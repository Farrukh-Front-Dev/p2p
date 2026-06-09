"""Review schemas."""
from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


class ReviewCreate(BaseModel):
    slot_id: uuid.UUID
    is_positive: bool
    comment: str | None = None


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slot_id: uuid.UUID
    author_id: uuid.UUID
    target_id: uuid.UUID
    is_positive: bool
    comment: str | None = None
