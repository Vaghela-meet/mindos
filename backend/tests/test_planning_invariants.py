import pytest
from datetime import time, datetime
from app.core.exceptions import PlanInvariantViolationException
from app.models.task import Task, TaskStatus, TaskPriority, TaskType
from app.models.availability import Availability, DayOfWeek
from app.models.daily_plan import ScheduleReasonCode
from app.services.planning.invariants import validate_plan_invariants
from app.services.planning.types import DraftBlock


def create_task(tid: int, status: TaskStatus = TaskStatus.TODO) -> Task:
    return Task(
        id=tid,
        goal_id=1,
        title=f"Task {tid}",
        status=status,
        priority=TaskPriority.MEDIUM,
        task_type=TaskType.SHALLOW_WORK,
        estimated_minutes=60,
    )


def create_window(start: time, end: time) -> Availability:
    return Availability(
        id=1,
        user_id=1,
        day_of_week=DayOfWeek.MONDAY,
        start_time=start,
        end_time=end,
    )


class TestPlanningInvariants:
    """Verifies that all architectural invariants are strictly enforced before DB persistence."""

    def test_valid_plan_passes_invariants(self):
        tasks = [create_task(1), create_task(2)]
        windows = [create_window(time(9, 0), time(12, 0))]
        blocks = [
            DraftBlock(1, "Task 1", TaskType.SHALLOW_WORK, time(9, 0), time(10, 0), 60, ScheduleReasonCode.PRIMARY_FIT),
            DraftBlock(2, "Task 2", TaskType.SHALLOW_WORK, time(10, 0), time(11, 0), 60, ScheduleReasonCode.PRIMARY_FIT),
        ]
        # Usable capacity = 120m
        validate_plan_invariants(
            user_id=1,
            usable_capacity_minutes=120,
            blocks=blocks,
            availability_windows=windows,
            candidate_tasks=tasks,
        )

    def test_overlapping_blocks_rejected(self):
        tasks = [create_task(1), create_task(2)]
        windows = [create_window(time(9, 0), time(12, 0))]
        # Overlapping: 09:00-10:30 and 10:00-11:00
        blocks = [
            DraftBlock(1, "Task 1", TaskType.SHALLOW_WORK, time(9, 0), time(10, 30), 90, ScheduleReasonCode.PRIMARY_FIT),
            DraftBlock(2, "Task 2", TaskType.SHALLOW_WORK, time(10, 0), time(11, 0), 60, ScheduleReasonCode.PRIMARY_FIT),
        ]
        with pytest.raises(PlanInvariantViolationException, match="Overlap detected"):
            validate_plan_invariants(1, 180, blocks, windows, tasks)

    def test_window_gap_crossing_rejected(self):
        tasks = [create_task(1)]
        # Two windows: 09:00-12:00 and 14:00-17:00 (Gap: 12:00-14:00)
        windows = [
            create_window(time(9, 0), time(12, 0)),
            create_window(time(14, 0), time(17, 0)),
        ]
        # Block crosses the gap: 11:30 - 14:30
        blocks = [
            DraftBlock(1, "Task 1", TaskType.SHALLOW_WORK, time(11, 30), time(14, 30), 180, ScheduleReasonCode.PRIMARY_FIT),
        ]
        with pytest.raises(PlanInvariantViolationException, match="inter-window gap"):
            validate_plan_invariants(1, 300, blocks, windows, tasks)

    def test_grid_unaligned_rejected(self):
        tasks = [create_task(1)]
        windows = [create_window(time(9, 0), time(12, 0))]
        # Starts at 09:15 (unaligned)
        blocks = [
            DraftBlock(1, "Task 1", TaskType.SHALLOW_WORK, time(9, 15), time(10, 15), 60, ScheduleReasonCode.PRIMARY_FIT),
        ]
        with pytest.raises(PlanInvariantViolationException, match="not aligned to 30-minute grid"):
            validate_plan_invariants(1, 180, blocks, windows, tasks)

    def test_capacity_ceiling_exceeded_rejected(self):
        tasks = [create_task(1)]
        windows = [create_window(time(9, 0), time(12, 0))]
        blocks = [
            DraftBlock(1, "Task 1", TaskType.SHALLOW_WORK, time(9, 0), time(11, 0), 120, ScheduleReasonCode.PRIMARY_FIT),
        ]
        # Usable capacity is only 90m, but 120m allocated
        with pytest.raises(PlanInvariantViolationException, match="exceeds usable capacity ceiling"):
            validate_plan_invariants(1, 90, blocks, windows, tasks)

    def test_completed_task_scheduled_rejected(self):
        tasks = [create_task(1, status=TaskStatus.COMPLETED)]
        windows = [create_window(time(9, 0), time(12, 0))]
        blocks = [
            DraftBlock(1, "Task 1", TaskType.SHALLOW_WORK, time(9, 0), time(10, 0), 60, ScheduleReasonCode.PRIMARY_FIT),
        ]
        with pytest.raises(PlanInvariantViolationException, match="terminal status"):
            validate_plan_invariants(1, 180, blocks, windows, tasks)
