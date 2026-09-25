import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, CheckConstraint, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TaskType(str, enum.Enum):
    ROUTINE = "ROUTINE"
    DEEP_WORK = "DEEP_WORK"
    SHALLOW_WORK = "SHALLOW_WORK"
    HABIT = "HABIT"
    DEADLINE_DRIVEN = "DEADLINE_DRIVEN"
    CREATIVE = "CREATIVE"
    ADMINISTRATIVE = "ADMINISTRATIVE"


class RecurrenceCadence(str, enum.Enum):
    DAILY = "DAILY"
    WEEKDAYS = "WEEKDAYS"
    WEEKLY = "WEEKLY"


class Task(Base, TimestampMixin):
    """
    Task entity representing granular execution work.
    Belongs to exactly one Goal.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="RESTRICT"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus, name="task_status"), default=TaskStatus.TODO, nullable=False, index=True)
    priority = Column(Enum(TaskPriority, name="task_priority"), default=TaskPriority.MEDIUM, nullable=False)
    task_type = Column(
        Enum(TaskType, name="task_type"),
        default=TaskType.SHALLOW_WORK,
        server_default="SHALLOW_WORK",
        nullable=False,
        index=True,
    )
    is_recurring = Column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )
    recurrence_cadence = Column(
        Enum(RecurrenceCadence, name="recurrence_cadence"),
        nullable=True,
    )
    estimated_minutes = Column(Integer, nullable=True)
    deadline = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Check constraint: estimated_minutes must be strictly positive when supplied
    __table_args__ = (
        CheckConstraint("estimated_minutes > 0", name="check_positive_estimated_minutes"),
    )

    # Relationships
    goal = relationship("Goal", back_populates="tasks")
    schedule_blocks = relationship("ScheduleBlock", back_populates="task", cascade="all, delete-orphan")
