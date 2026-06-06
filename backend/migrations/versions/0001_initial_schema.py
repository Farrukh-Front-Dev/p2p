"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column("username", sa.String(64), nullable=True),
        sa.Column("school21_login", sa.String(64), nullable=False),
        sa.Column("nickname", sa.String(64), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("language", sa.String(8), server_default="uz", nullable=False),
        sa.Column(
            "directions",
            postgresql.ARRAY(sa.String()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("coins", sa.Integer(), server_default="5", nullable=False),
        sa.Column("max_coins", sa.Integer(), server_default="15", nullable=False),
        sa.Column("xp", sa.Integer(), server_default="0", nullable=False),
        sa.Column("level", sa.Integer(), server_default="1", nullable=False),
        sa.Column("rating", sa.Float(), server_default="0", nullable=False),
        sa.Column("total_taught", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_learned", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_unique_constraint("uq_users_school21_login", "users", ["school21_login"])
    op.create_index("idx_users_school21_login", "users", ["school21_login"])

    op.create_table(
        "slots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mentor_id", sa.BigInteger(), sa.ForeignKey("users.id")),
        sa.Column(
            "mentee_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True
        ),
        sa.Column("direction", sa.String(64), nullable=False),
        sa.Column("title", sa.String(128), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(32), server_default="open", nullable=False),
        sa.Column(
            "reminder_sent", sa.Boolean(), server_default=sa.false(), nullable=False
        ),
        sa.Column(
            "reveal_sent", sa.Boolean(), server_default=sa.false(), nullable=False
        ),
        sa.Column("chat_group_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("idx_slots_status", "slots", ["status"])
    op.create_index("idx_slots_direction", "slots", ["direction"])
    op.create_index("idx_slots_start_time", "slots", ["start_time"])
    op.create_index("idx_slots_mentor_id", "slots", ["mentor_id"])

    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("slots.id")),
        sa.Column("mentor_id", sa.BigInteger(), sa.ForeignKey("users.id")),
        sa.Column("mentee_id", sa.BigInteger(), sa.ForeignKey("users.id")),
        sa.Column("chat_group_id", sa.BigInteger(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("finish_requested_by", sa.BigInteger(), nullable=True),
        sa.Column("mentor_comment", sa.Text(), nullable=True),
        sa.Column("mentee_comment", sa.Text(), nullable=True),
        sa.Column(
            "mentor_confirmed", sa.Boolean(), server_default=sa.false(), nullable=False
        ),
        sa.Column(
            "mentee_confirmed", sa.Boolean(), server_default=sa.false(), nullable=False
        ),
        sa.Column("mentor_rating", sa.Integer(), nullable=True),
        sa.Column("mentee_rating", sa.Integer(), nullable=True),
        sa.Column(
            "coins_transferred", sa.Boolean(), server_default=sa.false(), nullable=False
        ),
        sa.Column(
            "xp_awarded", sa.Boolean(), server_default=sa.false(), nullable=False
        ),
        sa.Column("status", sa.String(32), server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id")),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column(
            "slot_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("slots.id"),
            nullable=True,
        ),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sessions.id"),
            nullable=True,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sessions.id")
        ),
        sa.Column("reviewer_id", sa.BigInteger(), sa.ForeignKey("users.id")),
        sa.Column("reviewed_id", sa.BigInteger(), sa.ForeignKey("users.id")),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating_range"),
    )


def downgrade() -> None:
    op.drop_table("reviews")
    op.drop_table("transactions")
    op.drop_table("sessions")
    op.drop_index("idx_slots_mentor_id", table_name="slots")
    op.drop_index("idx_slots_start_time", table_name="slots")
    op.drop_index("idx_slots_direction", table_name="slots")
    op.drop_index("idx_slots_status", table_name="slots")
    op.drop_table("slots")
    op.drop_index("idx_users_school21_login", table_name="users")
    op.drop_constraint("uq_users_school21_login", "users", type_="unique")
    op.drop_table("users")
