from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.goal import GoalStatus, GoalPriority


class GoalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title of the goal")
    description: Optional[str] = Field(None, description="Detailed description of the goal")
    status: GoalStatus = Field(default=GoalStatus.ACTIVE, description="Current lifecycle state")
    priority: GoalPriority = Field(default=GoalPriority.MEDIUM, description="Importance level")
    deadline: Optional[datetime] = Field(None, description="Target completion timestamp")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Title cannot be empty or whitespace only")
        return stripped


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[GoalStatus] = None
    priority: Optional[GoalPriority] = None
    deadline: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Title cannot be empty or whitespace only")
            return stripped
        return v


class GoalResponse(GoalBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
