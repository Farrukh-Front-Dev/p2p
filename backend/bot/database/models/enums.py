"""Model status/type enumlari (String sifatida saqlanadi)."""

from __future__ import annotations

import enum


class SlotStatus(str, enum.Enum):
    OPEN = "open"
    BOOKED = "booked"
    REMINDED = "reminded"
    ACTIVE = "active"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    FINISHING = "finishing"
    FINISHED = "finished"
    DISPUTED = "disputed"


class TransactionType(str, enum.Enum):
    EARN_TEACH = "earn_teach"
    SPEND_LEARN = "spend_learn"
    BONUS = "bonus"
    PENALTY = "penalty"


class ReviewRole(str, enum.Enum):
    MENTOR = "mentor"
    MENTEE = "mentee"
