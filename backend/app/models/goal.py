import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class GoalStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class GoalPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Goal(Base, TimestampMixin):
    """
    Goal entity representing high-level intent and milestones.
    Belongs to exactly one User; owns zero or more Tasks.
    """
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(GoalStatus, name="goal_status"), default=GoalStatus.ACTIVE, nullable=False, index=True)
    priority = Column(Enum(GoalPriority, name="goal_priority"), default=GoalPriority.MEDIUM, nullable=False)
    deadline = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="goals")
    # Conservative deletion: Tasks are not automatically deleted when a Goal is deleted
    tasks = relationship("Task", back_populates="goal", passive_deletes="all")
