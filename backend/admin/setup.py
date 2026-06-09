"""SQLAdmin panel configuration."""
from __future__ import annotations

from fastapi import FastAPI
from sqladmin import Admin, ModelView

from app.db.base import engine
from app.db.models.leaderboard_snapshot import LeaderboardSnapshot
from app.db.models.notification import Notification
from app.db.models.review import Review
from app.db.models.slot import Slot
from app.db.models.user import User
from app.db.models.xp_log import XpLog


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.school21_login,
        User.telegram_username,
        User.campus,
        User.level,
        User.xp,
        User.peer_points,
        User.peer_coins,
        User.is_active,
        User.is_admin,
    ]
    column_searchable_list = [User.school21_login, User.telegram_username]
    column_sortable_list = [User.xp, User.level, User.created_at]
    name = "User"
    name_plural = "Users"


class SlotAdmin(ModelView, model=Slot):
    column_list = [
        Slot.id,
        Slot.reviewer_id,
        Slot.reviewee_id,
        Slot.reviewer_project,
        Slot.status,
        Slot.campus,
        Slot.is_online,
        Slot.start_time,
    ]
    column_sortable_list = [Slot.start_time, Slot.status]


class ReviewAdmin(ModelView, model=Review):
    column_list = [Review.id, Review.slot_id, Review.author_id, Review.is_positive]


class NotificationAdmin(ModelView, model=Notification):
    column_list = [
        Notification.id,
        Notification.user_id,
        Notification.type,
        Notification.is_read,
        Notification.sent_telegram,
    ]


class XpLogAdmin(ModelView, model=XpLog):
    column_list = [XpLog.id, XpLog.user_id, XpLog.amount, XpLog.reason, XpLog.created_at]


class LeaderboardSnapshotAdmin(ModelView, model=LeaderboardSnapshot):
    column_list = [
        LeaderboardSnapshot.id,
        LeaderboardSnapshot.month,
        LeaderboardSnapshot.category,
        LeaderboardSnapshot.rank,
        LeaderboardSnapshot.value,
    ]


def init_admin(app: FastAPI) -> Admin:
    admin = Admin(app, engine, title="P2P Admin")
    admin.add_view(UserAdmin)
    admin.add_view(SlotAdmin)
    admin.add_view(ReviewAdmin)
    admin.add_view(NotificationAdmin)
    admin.add_view(XpLogAdmin)
    admin.add_view(LeaderboardSnapshotAdmin)
    return admin
