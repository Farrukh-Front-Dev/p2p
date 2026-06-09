"""Platform-internal Peer Points & Peer Coins logic."""
from __future__ import annotations

from app.db.models.user import User

MAX_PEER_POINTS = 15


def add_peer_points(user: User, amount: int) -> None:
    """Adjust peer points with [0, 15] clamping and coin overflow conversion."""
    new_val = user.peer_points + amount
    if new_val > MAX_PEER_POINTS:
        overflow = new_val - MAX_PEER_POINTS
        user.peer_coins += overflow
        user.peer_points = MAX_PEER_POINTS
    elif new_val < 0:
        user.peer_points = 0
    else:
        user.peer_points = new_val


def add_peer_coins(user: User, amount: int) -> None:
    user.peer_coins = max(user.peer_coins + amount, 0)


def can_book_slot(user: User) -> bool:
    return user.peer_points > 0
