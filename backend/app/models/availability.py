import enum
from sqlalchemy import Column, Integer, Time, ForeignKey, Enum, CheckConstraint, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class DayOfWeek(str, enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class Availability(Base, TimestampMixin):
    """
    Availability entity representing a weekly recurring time window
    during which the user is generally available to work.
    """
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    day_of_week = Column(Enum(DayOfWeek, name="day_of_week"), nullable=False, index=True)
    start_time = Column(Time(timezone=False), nullable=False)
    end_time = Column(Time(timezone=False), nullable=False)

    # Relationships
    user = relationship("User", back_populates="availabilities")

    __table_args__ = (
        CheckConstraint("start_time < end_time", name="check_availability_start_before_end"),
        Index("ix_availability_user_weekday", "user_id", "day_of_week"),
    )
