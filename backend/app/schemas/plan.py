from datetime import date, time, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.models.task import TaskType
from app.models.daily_plan import (
    PlanStatus,
    BlockStatus,
    ScheduleReasonCode,
    ExclusionReasonCode,
)


class PlannerPolicy(BaseModel):
    """
    In-memory configuration policy governing planning constraints.
    """
    usable_capacity_ratio: float = Field(
        default=0.85,
        ge=0.1,
        le=1.0,
        description="Ratio of total availability usable for scheduled work (default 85%)",
    )
    minimum_deep_work_block: int = Field(
        default=60,
        ge=30,
        description="Minimum block size in minutes for DEEP_WORK and CREATIVE tasks",
    )
    minimum_standard_block: int = Field(
        default=30,
        ge=30,
        description="Minimum block size in minutes for standard tasks",
    )
    max_daily_task_blocks: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Maximum number of schedule blocks a single task can be split into in one day",
    )
    scheduling_grid_minutes: int = Field(
        default=30,
        ge=15,
        le=60,
        description="Grid resolution in minutes (locked to 30m in M3)",
    )


class ShortfallRecord(BaseModel):
    task_id: int
    task_title: str
    unscheduled_minutes: int
    reason_code: ExclusionReasonCode


class ShortfallReport(BaseModel):
    total_shortfall_minutes: int
    usable_capacity_minutes: int
    records: List[ShortfallRecord] = Field(default_factory=list)


class ScheduleBlockBase(BaseModel):
    task_id: int
    start_time: time
    end_time: time
    duration_minutes: int
    status: BlockStatus = BlockStatus.PLANNED
    schedule_reason_code: ScheduleReasonCode


class ScheduleBlockResponse(ScheduleBlockBase):
    id: int
    plan_id: int
    task_title: Optional[str] = None
    task_type: Optional[TaskType] = None
    goal_title: Optional[str] = None
    goal_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailyPlanBase(BaseModel):
    plan_date: date
    status: PlanStatus = PlanStatus.DRAFT
    usable_capacity_minutes: int = 0
    allocated_minutes: int = 0
    buffer_minutes: int = 0
    shortfall_minutes: int = 0
    notes: Optional[str] = None


class DailyPlanResponse(DailyPlanBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    blocks: List[ScheduleBlockResponse] = Field(default_factory=list)
    shortfall_report: Optional[ShortfallReport] = None

    model_config = ConfigDict(from_attributes=True)


class PlanGenerationRequest(BaseModel):
    plan_date: Optional[date] = Field(None, description="Target calendar date to plan for (defaults to today)")
    policy: Optional[PlannerPolicy] = Field(None, description="Optional custom policy parameters")
