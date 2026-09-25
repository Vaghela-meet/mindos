"""Pydantic schemas package."""

from app.schemas.health import HealthCheckResponse, DatabaseStatus
from app.schemas.goal import GoalBase, GoalCreate, GoalUpdate, GoalResponse
from app.schemas.task import TaskBase, TaskCreate, TaskUpdate, TaskResponse
from app.schemas.availability import (
    AvailabilityBase,
    AvailabilityCreate,
    AvailabilityUpdate,
    AvailabilityResponse,
)
from app.schemas.plan import (
    PlannerPolicy,
    ShortfallRecord,
    ShortfallReport,
    ScheduleBlockBase,
    ScheduleBlockResponse,
    DailyPlanBase,
    DailyPlanResponse,
    PlanGenerationRequest,
)

__all__ = [
    "HealthCheckResponse",
    "DatabaseStatus",
    "GoalBase",
    "GoalCreate",
    "GoalUpdate",
    "GoalResponse",
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "AvailabilityBase",
    "AvailabilityCreate",
    "AvailabilityUpdate",
    "AvailabilityResponse",
    "PlannerPolicy",
    "ShortfallRecord",
    "ShortfallReport",
    "ScheduleBlockBase",
    "ScheduleBlockResponse",
    "DailyPlanBase",
    "DailyPlanResponse",
    "PlanGenerationRequest",
]
