from datetime import time
from typing import List, Sequence, Union
from app.core.exceptions import PlanInvariantViolationException
from app.models.availability import Availability
from app.models.daily_plan import DailyPlan, ScheduleBlock, ScheduleReasonCode
from app.models.task import Task, TaskStatus
from app.services.planning.types import DraftBlock, time_to_minutes


def validate_plan_invariants(
    user_id: int,
    usable_capacity_minutes: int,
    blocks: Sequence[Union[ScheduleBlock, DraftBlock]],
    availability_windows: Sequence[Availability],
    candidate_tasks: Sequence[Task],
) -> None:
    """
    Validates all architectural invariants on a proposed plan before persistence.
    Raises PlanInvariantViolationException if any invariant is violated.
    """
    task_map = {t.id: t for t in candidate_tasks}

    # 1. Temporal Validity
    for b in blocks:
        s_min = time_to_minutes(b.start_time)
        e_min = time_to_minutes(b.end_time)
        if s_min >= e_min:
            raise PlanInvariantViolationException(
                f"Block for task {b.task_id} has invalid times: {b.start_time} >= {b.end_time}"
            )
        if b.duration_minutes <= 0:
            raise PlanInvariantViolationException(
                f"Block for task {b.task_id} has non-positive duration: {b.duration_minutes}m"
            )
        if (e_min - s_min) != b.duration_minutes:
            raise PlanInvariantViolationException(
                f"Block duration mismatch for task {b.task_id}: {b.duration_minutes}m != {e_min - s_min}m"
            )

    # 2. Grid Alignment (30-minute grid)
    for b in blocks:
        if b.start_time.minute not in (0, 30) or b.start_time.second != 0:
            raise PlanInvariantViolationException(
                f"Block start_time {b.start_time} is not aligned to 30-minute grid"
            )
        if b.end_time.minute not in (0, 30) or b.end_time.second != 0:
            raise PlanInvariantViolationException(
                f"Block end_time {b.end_time} is not aligned to 30-minute grid"
            )
        if b.duration_minutes % 30 != 0:
            raise PlanInvariantViolationException(
                f"Block duration {b.duration_minutes} is not a multiple of 30 minutes"
            )

    # 3. Zero Overlap
    sorted_blocks = sorted(blocks, key=lambda b: time_to_minutes(b.start_time))
    for i in range(len(sorted_blocks) - 1):
        curr = sorted_blocks[i]
        nxt = sorted_blocks[i + 1]
        if time_to_minutes(curr.end_time) > time_to_minutes(nxt.start_time):
            raise PlanInvariantViolationException(
                f"Overlap detected between task {curr.task_id} ({curr.start_time}-{curr.end_time}) "
                f"and task {nxt.task_id} ({nxt.start_time}-{nxt.end_time})"
            )

    # 4. Window Containment & No Gap Crossing
    # Merged continuous windows (touching boundary windows merge)
    sorted_windows = sorted(availability_windows, key=lambda w: time_to_minutes(w.start_time))
    merged_ranges: List[tuple[int, int]] = []
    for w in sorted_windows:
        w_start = time_to_minutes(w.start_time)
        w_end = time_to_minutes(w.end_time)
        if not merged_ranges:
            merged_ranges.append((w_start, w_end))
        else:
            prev_start, prev_end = merged_ranges[-1]
            if w_start <= prev_end:
                merged_ranges[-1] = (prev_start, max(prev_end, w_end))
            else:
                merged_ranges.append((w_start, w_end))

    for b in blocks:
        b_start = time_to_minutes(b.start_time)
        b_end = time_to_minutes(b.end_time)
        contained = any(r_start <= b_start and b_end <= r_end for r_start, r_end in merged_ranges)
        if not contained:
            raise PlanInvariantViolationException(
                f"Block for task {b.task_id} ({b.start_time}-{b.end_time}) is not wholly contained "
                f"within user availability windows or crosses an inter-window gap"
            )

    # 5. Capacity Ceiling Adherence
    total_block_minutes = sum(b.duration_minutes for b in blocks)
    if total_block_minutes > usable_capacity_minutes:
        raise PlanInvariantViolationException(
            f"Total scheduled minutes ({total_block_minutes}m) exceeds usable capacity ceiling "
            f"({usable_capacity_minutes}m)"
        )

    # 6. Task Status Validity
    for b in blocks:
        task = task_map.get(b.task_id)
        if task and task.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
            raise PlanInvariantViolationException(
                f"Cannot schedule task {b.task_id} with terminal status {task.status}"
            )

    # 7. Reason Code Completeness
    for b in blocks:
        if not b.schedule_reason_code or not isinstance(b.schedule_reason_code, ScheduleReasonCode):
            raise PlanInvariantViolationException(
                f"Block for task {b.task_id} missing valid ScheduleReasonCode"
            )
