from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class User(Base, TimestampMixin):
    """
    User entity representing system user and domain ownership boundary.
    Authentication is omitted in M1; this model establishes data ownership.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    name = Column(String(100), nullable=False)
    timezone = Column(String(50), nullable=False, default="UTC")

    # Relationship: 1 User -> Many Goals
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    # Relationship: 1 User -> Many Availabilities
    availabilities = relationship("Availability", back_populates="user", cascade="all, delete-orphan")
    # Relationship: 1 User -> Many DailyPlans
    daily_plans = relationship("DailyPlan", back_populates="user", cascade="all, delete-orphan")
