"""SQLAlchemy models package. Import all models so Alembic can discover them."""
from app.db.models.user import User
from app.db.models.slot import Slot
from app.db.models.review import Review
from app.db.models.notification import Notification
from app.db.models.xp_log import XpLog
from app.db.models.leaderboard_snapshot import LeaderboardSnapshot

__all__ = [
    "User",
    "Slot",
    "Review",
    "Notification",
    "XpLog",
    "LeaderboardSnapshot",
]
