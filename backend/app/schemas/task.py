from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.task import TaskStatus, TaskPriority, TaskType, RecurrenceCadence


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title of the task")
    description: Optional[str] = Field(None, description="Detailed description")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Current lifecycle state")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Importance level")
    task_type: TaskType = Field(default=TaskType.SHALLOW_WORK, description="Cognitive modality of work")
    is_recurring: bool = Field(default=False, description="Whether this task recurs")
    recurrence_cadence: Optional[RecurrenceCadence] = Field(None, description="Cadence if recurring")
    estimated_minutes: Optional[int] = Field(None, description="Estimated duration in minutes (> 0)")
    deadline: Optional[datetime] = Field(None, description="Due date and time")
    completed_at: Optional[datetime] = Field(None, description="Timestamp when task was marked completed")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Title cannot be empty or whitespace only")
        return stripped

    @field_validator("estimated_minutes")
    @classmethod
    def validate_estimated_minutes(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("Estimated minutes must be strictly positive (> 0)")
        return v


class TaskCreate(TaskBase):
    goal_id: int = Field(..., description="Foreign key reference to parent Goal")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    task_type: Optional[TaskType] = None
    is_recurring: Optional[bool] = None
    recurrence_cadence: Optional[RecurrenceCadence] = None
    estimated_minutes: Optional[int] = None
    deadline: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Title cannot be empty or whitespace only")
            return stripped
        return v

    @field_validator("estimated_minutes")
    @classmethod
    def validate_estimated_minutes(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("Estimated minutes must be strictly positive (> 0)")
        return v


class TaskResponse(TaskBase):
    id: int
    goal_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
