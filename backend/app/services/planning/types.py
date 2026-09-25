from dataclasses import dataclass, field
from datetime import date, time, datetime
from typing import List, Optional
from app.models.task import TaskType
from app.models.daily_plan import BlockStatus, ScheduleReasonCode
from app.schemas.plan import ShortfallReport


def time_to_minutes(t: time) -> int:
    """Converts a datetime.time to minutes from midnight."""
    return t.hour * 60 + t.minute


def minutes_to_time(m: int) -> time:
    """Converts minutes from midnight to a datetime.time."""
    hours = (m // 60) % 24
    minutes = m % 60
    return time(hour=hours, minute=minutes)


@dataclass(frozen=True)
class TimeSlot:
    """Represents a discrete 30-minute scheduling slot."""
    start_time: time
    end_time: time
    duration_minutes: int = 30

    @property
    def start_minutes(self) -> int:
        return time_to_minutes(self.start_time)

    @property
    def end_minutes(self) -> int:
        return time_to_minutes(self.end_time)


@dataclass
class SlotRun:
    """
    Represents a contiguous sequence of 30-minute slots inside a single availability window.
    Inter-window gaps are never part of a SlotRun.
    """
    slots: List[TimeSlot] = field(default_factory=list)
    allocated_count: int = 0

    @property
    def total_slots(self) -> int:
        return len(self.slots)

    @property
    def remaining_slots(self) -> int:
        return max(0, len(self.slots) - self.allocated_count)

    def get_unallocated_slots(self) -> List[TimeSlot]:
        return self.slots[self.allocated_count:]

    def consume_slots(self, count: int) -> List[TimeSlot]:
        if count <= 0:
            return []
        available = self.get_unallocated_slots()
        take = min(count, len(available))
        consumed = available[:take]
        self.allocated_count += take
        return consumed


@dataclass
class DraftBlock:
    """In-memory representation of a planned schedule block before DB persistence."""
    task_id: int
    task_title: str
    task_type: TaskType
    start_time: time
    end_time: time
    duration_minutes: int
    schedule_reason_code: ScheduleReasonCode
    goal_id: Optional[int] = None
    goal_title: Optional[str] = None
    status: BlockStatus = BlockStatus.PLANNED


@dataclass
class PlanningResult:
    """Pure domain result from deterministic plan generation."""
    user_id: int
    plan_date: date
    usable_capacity_minutes: int
    allocated_minutes: int
    buffer_minutes: int
    shortfall_minutes: int
    blocks: List[DraftBlock] = field(default_factory=list)
    shortfall_report: Optional[ShortfallReport] = None
