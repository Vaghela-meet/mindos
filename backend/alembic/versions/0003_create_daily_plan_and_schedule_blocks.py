"""create daily plan and schedule blocks tables with task extensions

Revision ID: 0003_planning_engine
Revises: 0002_availability
Create Date: 2026-09-25 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "0003_planning_engine"
down_revision: Union[str, None] = "0002_availability"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Enums explicitly in PostgreSQL
    task_type_enum = postgresql.ENUM(
        "ROUTINE",
        "DEEP_WORK",
        "SHALLOW_WORK",
        "HABIT",
        "DEADLINE_DRIVEN",
        "CREATIVE",
        "ADMINISTRATIVE",
        name="task_type",
    )
    recurrence_cadence_enum = postgresql.ENUM(
        "DAILY",
        "WEEKDAYS",
        "WEEKLY",
        name="recurrence_cadence",
    )
    plan_status_enum = postgresql.ENUM(
        "DRAFT",
        "ACTIVE",
        "SUPERSEDED",
        "CANCELLED",
        name="plan_status",
    )
    block_status_enum = postgresql.ENUM(
        "PLANNED",
        "IN_PROGRESS",
        "COMPLETED",
        "SKIPPED",
        "CANCELLED",
        name="block_status",
    )
    schedule_reason_code_enum = postgresql.ENUM(
        "PRIMARY_FIT",
        "DEADLINE_PRESSURE_IMMINENT",
        "DEADLINE_PRESSURE_APPROACHING",
        "DEADLINE_PRESSURE_OVERDUE",
        "GOAL_ALIGNMENT_HIGH",
        "TASK_PRIORITY_HIGH",
        "CONTEXT_CONTINUITY",
        "TASK_IN_PROGRESS",
        "GAP_FILL_ROUTINE",
        "PARTIAL_WINDOW_SPLIT",
        name="schedule_reason_code",
    )

    task_type_enum.create(op.get_bind(), checkfirst=True)
    recurrence_cadence_enum.create(op.get_bind(), checkfirst=True)
    plan_status_enum.create(op.get_bind(), checkfirst=True)
    block_status_enum.create(op.get_bind(), checkfirst=True)
    schedule_reason_code_enum.create(op.get_bind(), checkfirst=True)

    # 2. Add columns to tasks table
    op.add_column(
        "tasks",
        sa.Column(
            "task_type",
            postgresql.ENUM(
                "ROUTINE",
                "DEEP_WORK",
                "SHALLOW_WORK",
                "HABIT",
                "DEADLINE_DRIVEN",
                "CREATIVE",
                "ADMINISTRATIVE",
                name="task_type",
                create_type=False,
            ),
            nullable=False,
            server_default="SHALLOW_WORK",
        ),
    )
    op.add_column(
        "tasks",
        sa.Column(
            "is_recurring",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )
    op.add_column(
        "tasks",
        sa.Column(
            "recurrence_cadence",
            postgresql.ENUM(
                "DAILY",
                "WEEKDAYS",
                "WEEKLY",
                name="recurrence_cadence",
                create_type=False,
            ),
            nullable=True,
        ),
    )
    op.create_index("ix_tasks_task_type", "tasks", ["task_type"])

    # 3. Create daily_plans table
    op.create_table(
        "daily_plans",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plan_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "DRAFT",
                "ACTIVE",
                "SUPERSEDED",
                "CANCELLED",
                name="plan_status",
                create_type=False,
            ),
            nullable=False,
            server_default="DRAFT",
        ),
        sa.Column("usable_capacity_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("allocated_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("buffer_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("shortfall_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_daily_plans_id", "daily_plans", ["id"])
    op.create_index("ix_daily_plans_user_id", "daily_plans", ["user_id"])
    op.create_index("ix_daily_plans_plan_date", "daily_plans", ["plan_date"])
    op.create_index("ix_daily_plans_status", "daily_plans", ["status"])
    op.create_index("ix_daily_plans_user_date", "daily_plans", ["user_id", "plan_date"])

    # 4. Create schedule_blocks table
    op.create_table(
        "schedule_blocks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(timezone=False), nullable=False),
        sa.Column("end_time", sa.Time(timezone=False), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "PLANNED",
                "IN_PROGRESS",
                "COMPLETED",
                "SKIPPED",
                "CANCELLED",
                name="block_status",
                create_type=False,
            ),
            nullable=False,
            server_default="PLANNED",
        ),
        sa.Column(
            "schedule_reason_code",
            postgresql.ENUM(
                "PRIMARY_FIT",
                "DEADLINE_PRESSURE_IMMINENT",
                "DEADLINE_PRESSURE_APPROACHING",
                "DEADLINE_PRESSURE_OVERDUE",
                "GOAL_ALIGNMENT_HIGH",
                "TASK_PRIORITY_HIGH",
                "CONTEXT_CONTINUITY",
                "TASK_IN_PROGRESS",
                "GAP_FILL_ROUTINE",
                "PARTIAL_WINDOW_SPLIT",
                name="schedule_reason_code",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["daily_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("start_time < end_time", name="check_block_start_before_end"),
        sa.CheckConstraint("duration_minutes > 0", name="check_block_positive_duration"),
    )
    op.create_index("ix_schedule_blocks_id", "schedule_blocks", ["id"])
    op.create_index("ix_schedule_blocks_plan_id", "schedule_blocks", ["plan_id"])
    op.create_index("ix_schedule_blocks_task_id", "schedule_blocks", ["task_id"])
    op.create_index("ix_schedule_blocks_plan_start", "schedule_blocks", ["plan_id", "start_time"])


def downgrade() -> None:
    # 1. Drop schedule_blocks
    op.drop_index("ix_schedule_blocks_plan_start", table_name="schedule_blocks")
    op.drop_index("ix_schedule_blocks_task_id", table_name="schedule_blocks")
    op.drop_index("ix_schedule_blocks_plan_id", table_name="schedule_blocks")
    op.drop_index("ix_schedule_blocks_id", table_name="schedule_blocks")
    op.drop_table("schedule_blocks")

    # 2. Drop daily_plans
    op.drop_index("ix_daily_plans_user_date", table_name="daily_plans")
    op.drop_index("ix_daily_plans_status", table_name="daily_plans")
    op.drop_index("ix_daily_plans_plan_date", table_name="daily_plans")
    op.drop_index("ix_daily_plans_user_id", table_name="daily_plans")
    op.drop_index("ix_daily_plans_id", table_name="daily_plans")
    op.drop_table("daily_plans")

    # 3. Drop columns from tasks
    op.drop_index("ix_tasks_task_type", table_name="tasks")
    op.drop_column("tasks", "recurrence_cadence")
    op.drop_column("tasks", "is_recurring")
    op.drop_column("tasks", "task_type")

    # 4. Drop enums
    op.execute("DROP TYPE IF EXISTS schedule_reason_code")
    op.execute("DROP TYPE IF EXISTS block_status")
    op.execute("DROP TYPE IF EXISTS plan_status")
    op.execute("DROP TYPE IF EXISTS recurrence_cadence")
    op.execute("DROP TYPE IF EXISTS task_type")
