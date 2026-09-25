import enum
from sqlalchemy import Column, Integer, Date, Time, Text, ForeignKey, Enum, CheckConstraint, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class PlanStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    CANCELLED = "CANCELLED"


class BlockStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"


class ScheduleReasonCode(str, enum.Enum):
    PRIMARY_FIT = "PRIMARY_FIT"
    DEADLINE_PRESSURE_IMMINENT = "DEADLINE_PRESSURE_IMMINENT"
    DEADLINE_PRESSURE_APPROACHING = "DEADLINE_PRESSURE_APPROACHING"
    DEADLINE_PRESSURE_OVERDUE = "DEADLINE_PRESSURE_OVERDUE"
    GOAL_ALIGNMENT_HIGH = "GOAL_ALIGNMENT_HIGH"
    TASK_PRIORITY_HIGH = "TASK_PRIORITY_HIGH"
    CONTEXT_CONTINUITY = "CONTEXT_CONTINUITY"
    TASK_IN_PROGRESS = "TASK_IN_PROGRESS"
    GAP_FILL_ROUTINE = "GAP_FILL_ROUTINE"
    PARTIAL_WINDOW_SPLIT = "PARTIAL_WINDOW_SPLIT"


class ExclusionReasonCode(str, enum.Enum):
    INSUFFICIENT_CAPACITY = "INSUFFICIENT_CAPACITY"
    LOWER_PRIORITY = "LOWER_PRIORITY"
    WINDOW_TOO_SMALL = "WINDOW_TOO_SMALL"
    DEADLINE_OUTSIDE_HORIZON = "DEADLINE_OUTSIDE_HORIZON"
    MAX_DAILY_SPLITS_REACHED = "MAX_DAILY_SPLITS_REACHED"
    NO_AVAILABILITY = "NO_AVAILABILITY"
    NO_ACTIONABLE_TASKS = "NO_ACTIONABLE_TASKS"


class DailyPlan(Base, TimestampMixin):
    """
    DailyPlan entity representing a concrete, chronological commitment of attention
    for a user on a specific calendar date.
    """
    __tablename__ = "daily_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_date = Column(Date, nullable=False, index=True)
    status = Column(Enum(PlanStatus, name="plan_status"), default=PlanStatus.DRAFT, nullable=False, index=True)
    usable_capacity_minutes = Column(Integer, default=0, nullable=False)
    allocated_minutes = Column(Integer, default=0, nullable=False)
    buffer_minutes = Column(Integer, default=0, nullable=False)
    shortfall_minutes = Column(Integer, default=0, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="daily_plans")
    blocks = relationship(
        "ScheduleBlock",
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="ScheduleBlock.start_time",
    )

    __table_args__ = (
        Index("ix_daily_plans_user_date", "user_id", "plan_date"),
    )


class ScheduleBlock(Base, TimestampMixin):
    """
    ScheduleBlock entity representing a discrete, non-overlapping block of scheduled work
    anchored to the 30-minute grid.
    """
    __tablename__ = "schedule_blocks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("daily_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    start_time = Column(Time(timezone=False), nullable=False)
    end_time = Column(Time(timezone=False), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(Enum(BlockStatus, name="block_status"), default=BlockStatus.PLANNED, nullable=False)
    schedule_reason_code = Column(Enum(ScheduleReasonCode, name="schedule_reason_code"), nullable=False)

    # Relationships
    plan = relationship("DailyPlan", back_populates="blocks")
    task = relationship("Task", back_populates="schedule_blocks")

    __table_args__ = (
        CheckConstraint("start_time < end_time", name="check_block_start_before_end"),
        CheckConstraint("duration_minutes > 0", name="check_block_positive_duration"),
        Index("ix_schedule_blocks_plan_start", "plan_id", "start_time"),
    )
