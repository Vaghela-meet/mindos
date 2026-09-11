"""create availability table

Revision ID: 0002_availability
Revises: 0001_user_goal_task
Create Date: 2026-09-11 19:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0002_availability"
down_revision: Union[str, None] = "0001_user_goal_task"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create availability table
    op.create_table(
        "availability",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "day_of_week",
            sa.Enum(
                "MONDAY",
                "TUESDAY",
                "WEDNESDAY",
                "THURSDAY",
                "FRIDAY",
                "SATURDAY",
                "SUNDAY",
                name="day_of_week",
            ),
            nullable=False,
        ),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "start_time < end_time",
            name="check_availability_start_before_end",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 2. Indexes
    op.create_index(op.f("ix_availability_id"), "availability", ["id"], unique=False)
    op.create_index(op.f("ix_availability_user_id"), "availability", ["user_id"], unique=False)
    op.create_index(op.f("ix_availability_day_of_week"), "availability", ["day_of_week"], unique=False)
    op.create_index(
        "ix_availability_user_weekday",
        "availability",
        ["user_id", "day_of_week"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_availability_user_weekday", table_name="availability")
    op.drop_index(op.f("ix_availability_day_of_week"), table_name="availability")
    op.drop_index(op.f("ix_availability_user_id"), table_name="availability")
    op.drop_index(op.f("ix_availability_id"), table_name="availability")
    op.drop_table("availability")
    sa.Enum(name="day_of_week").drop(op.get_bind(), checkfirst=True)
