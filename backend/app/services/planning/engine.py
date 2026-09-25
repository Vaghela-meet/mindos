import math
from collections import defaultdict
from datetime import date, time
from typing import List, Optional, Dict
from app.models.task import Task, TaskStatus, TaskType
from app.models.goal import Goal
from app.models.availability import Availability
from app.models.daily_plan import (
    ScheduleReasonCode,
    ExclusionReasonCode,
    BlockStatus,
)
from app.schemas.plan import PlannerPolicy, ShortfallRecord, ShortfallReport
from app.services.planning.types import (
    TimeSlot,
    SlotRun,
    DraftBlock,
    PlanningResult,
    time_to_minutes,
    minutes_to_time,
)
from app.services.planning.sorter import (
    candidate_sort_key,
    determine_schedule_reason,
)


def build_slot_runs_from_availability(
    availability_windows: List[Availability],
    grid_minutes: int = 30,
) -> List[SlotRun]:
    """
    Constructs contiguous slot runs from availability windows.
    - Boundary-touching windows (e.g. 09:00-12:00 and 12:00-15:00) merge into a single continuous run.
    - Disjoint windows separated by gaps (e.g. 09:00-12:00 and 14:00-17:00) remain strictly separate runs.
    - Inter-window gaps contain no slots, preventing any cross-gap bridging.
    """
    if not availability_windows:
        return []

    # Sort windows strictly by start_time
    sorted_windows = sorted(availability_windows, key=lambda w: time_to_minutes(w.start_time))

    # Merge adjacent/contiguous windows
    merged_ranges: List[tuple[int, int]] = []
    for w in sorted_windows:
        w_start = time_to_minutes(w.start_time)
        w_end = time_to_minutes(w.end_time)

        if not merged_ranges:
            merged_ranges.append((w_start, w_end))
        else:
            prev_start, prev_end = merged_ranges[-1]
            if w_start <= prev_end:
                # Touching or overlapping (M2 prevents overlap, but touching w_start == prev_end merges)
                merged_ranges[-1] = (prev_start, max(prev_end, w_end))
            else:
                merged_ranges.append((w_start, w_end))

    slot_runs: List[SlotRun] = []
    for r_start, r_end in merged_ranges:
        slots: List[TimeSlot] = []
        curr = r_start
        while curr + grid_minutes <= r_end:
            slot_s = minutes_to_time(curr)
            slot_e = minutes_to_time(curr + grid_minutes)
            slots.append(TimeSlot(start_time=slot_s, end_time=slot_e, duration_minutes=grid_minutes))
            curr += grid_minutes

        if slots:
            slot_runs.append(SlotRun(slots=slots))

    return slot_runs


def generate_deterministic_daily_plan(
    user_id: int,
    plan_date: date,
    user_timezone: str,
    availability_windows: List[Availability],
    candidate_tasks: List[Task],
    active_goals: List[Goal],
    policy: Optional[PlannerPolicy] = None,
) -> PlanningResult:
    """
    Pure side-effect-free deterministic planning engine function.
    Converts inputs into a concrete DailyPlan, ScheduleBlocks, and ShortfallReport.
    """
    if policy is None:
        policy = PlannerPolicy()

    # Phase 1: Ingest & Pre-Checks
    if not availability_windows:
        return PlanningResult(
            user_id=user_id,
            plan_date=plan_date,
            usable_capacity_minutes=0,
            allocated_minutes=0,
            buffer_minutes=0,
            shortfall_minutes=0,
            blocks=[],
            shortfall_report=ShortfallReport(
                total_shortfall_minutes=0,
                usable_capacity_minutes=0,
                records=[
                    ShortfallRecord(
                        task_id=0,
                        task_title="User Availability",
                        unscheduled_minutes=0,
                        reason_code=ExclusionReasonCode.NO_AVAILABILITY,
                    )
                ] if candidate_tasks else [],
            ),
        )

    # Filter actionable candidate tasks
    actionable_tasks = [
        t for t in candidate_tasks if t.status in (TaskStatus.TODO, TaskStatus.IN_PROGRESS)
    ]
    if not actionable_tasks:
        raw_runs = build_slot_runs_from_availability(availability_windows, policy.scheduling_grid_minutes)
        total_raw = sum(run.total_slots * policy.scheduling_grid_minutes for run in raw_runs)
        usable = math.floor((total_raw * policy.usable_capacity_ratio) / policy.scheduling_grid_minutes) * policy.scheduling_grid_minutes
        buffer = total_raw - usable

        return PlanningResult(
            user_id=user_id,
            plan_date=plan_date,
            usable_capacity_minutes=usable,
            allocated_minutes=0,
            buffer_minutes=buffer,
            shortfall_minutes=0,
            blocks=[],
            shortfall_report=ShortfallReport(
                total_shortfall_minutes=0,
                usable_capacity_minutes=usable,
                records=[],
            ),
        )

    # Phase 2: Build Contiguous Slot Runs per Availability Window
    slot_runs = build_slot_runs_from_availability(availability_windows, policy.scheduling_grid_minutes)
    total_raw_minutes = sum(run.total_slots * policy.scheduling_grid_minutes for run in slot_runs)

    # Phase 3: Capacity Calculation & Ceiling Cap
    usable_capacity_minutes = (
        math.floor((total_raw_minutes * policy.usable_capacity_ratio) / policy.scheduling_grid_minutes)
        * policy.scheduling_grid_minutes
    )
    max_slots_to_allocate = usable_capacity_minutes // policy.scheduling_grid_minutes
    buffer_minutes = total_raw_minutes - usable_capacity_minutes

    # Phase 4: Candidate Sorting
    goals_by_id: Dict[int, Goal] = {g.id: g for g in active_goals}

    # Track remaining effort for each candidate
    task_remaining_effort: Dict[int, int] = {}
    for t in actionable_tasks:
        effort = t.estimated_minutes if (t.estimated_minutes and t.estimated_minutes > 0) else policy.scheduling_grid_minutes
        task_remaining_effort[t.id] = effort

    # Stable initial sort of candidates
    sorted_candidates = sorted(
        actionable_tasks,
        key=lambda t: candidate_sort_key(t, goals_by_id.get(t.goal_id), plan_date),
    )

    # Phase 5: Window-Aware Slot Allocation
    schedule_blocks: List[DraftBlock] = []
    unscheduled_records: List[ShortfallRecord] = []
    allocated_slots_count = 0
    task_splits_count: Dict[int, int] = defaultdict(int)

    last_goal_id: Optional[int] = None
    last_task_type: Optional[TaskType] = None

    for task in sorted_candidates:
        goal = goals_by_id.get(task.goal_id)

        if allocated_slots_count >= max_slots_to_allocate:
            unscheduled_records.append(
                ShortfallRecord(
                    task_id=task.id,
                    task_title=task.title,
                    unscheduled_minutes=task_remaining_effort[task.id],
                    reason_code=ExclusionReasonCode.INSUFFICIENT_CAPACITY,
                )
            )
            continue

        needed_slots = math.ceil(task_remaining_effort[task.id] / policy.scheduling_grid_minutes)

        # Minimum block size policy
        if task.task_type in (TaskType.DEEP_WORK, TaskType.CREATIVE):
            min_block_minutes = policy.minimum_deep_work_block
        else:
            min_block_minutes = policy.minimum_standard_block
        min_block_slots = max(1, min_block_minutes // policy.scheduling_grid_minutes)

        task_fully_scheduled = False

        for run in slot_runs:
            available_in_run = run.remaining_slots
            capacity_left_today = max_slots_to_allocate - allocated_slots_count
            effective_available = min(available_in_run, capacity_left_today)

            if effective_available <= 0:
                continue

            # Case A: Fits completely within the run
            if needed_slots <= effective_available:
                slots = run.consume_slots(needed_slots)
                start_t = slots[0].start_time
                end_t = slots[-1].end_time
                dur = len(slots) * policy.scheduling_grid_minutes

                is_split = task_splits_count[task.id] > 0
                is_continuity = (last_goal_id is not None and task.goal_id == last_goal_id)
                reason = determine_schedule_reason(
                    task,
                    goal,
                    plan_date,
                    is_split=is_split,
                    is_continuity=is_continuity,
                )

                block = DraftBlock(
                    task_id=task.id,
                    task_title=task.title,
                    task_type=task.task_type,
                    start_time=start_t,
                    end_time=end_t,
                    duration_minutes=dur,
                    schedule_reason_code=reason,
                    goal_id=task.goal_id,
                    goal_title=goal.title if goal else None,
                    status=BlockStatus.PLANNED,
                )
                schedule_blocks.append(block)
                allocated_slots_count += needed_slots
                task_remaining_effort[task.id] = 0
                last_goal_id = task.goal_id
                last_task_type = task.task_type
                task_fully_scheduled = True
                break

            # Case B: Cannot fit completely, evaluate task splitting across window runs
            can_split = (
                task_splits_count[task.id] < policy.max_daily_task_blocks
                and effective_available >= min_block_slots
            )

            if can_split:
                slots_to_take = min(needed_slots, effective_available)
                slots = run.consume_slots(slots_to_take)
                start_t = slots[0].start_time
                end_t = slots[-1].end_time
                dur = len(slots) * policy.scheduling_grid_minutes

                is_split = task_splits_count[task.id] > 0
                is_continuity = (last_goal_id is not None and task.goal_id == last_goal_id)
                reason = (
                    ScheduleReasonCode.PARTIAL_WINDOW_SPLIT
                    if is_split
                    else determine_schedule_reason(
                        task,
                        goal,
                        plan_date,
                        is_split=False,
                        is_continuity=is_continuity,
                    )
                )

                block = DraftBlock(
                    task_id=task.id,
                    task_title=task.title,
                    task_type=task.task_type,
                    start_time=start_t,
                    end_time=end_t,
                    duration_minutes=dur,
                    schedule_reason_code=reason,
                    goal_id=task.goal_id,
                    goal_title=goal.title if goal else None,
                    status=BlockStatus.PLANNED,
                )
                schedule_blocks.append(block)
                allocated_slots_count += slots_to_take
                task_splits_count[task.id] += 1
                task_remaining_effort[task.id] = max(0, task_remaining_effort[task.id] - dur)
                needed_slots -= slots_to_take
                last_goal_id = task.goal_id
                last_task_type = task.task_type

                if task_remaining_effort[task.id] == 0:
                    task_fully_scheduled = True
                    break

        # Record shortfall if task was completely excluded or only partially accommodated
        scheduled_for_task = [b for b in schedule_blocks if b.task_id == task.id]
        if not scheduled_for_task:
            # Task had zero slots scheduled
            if allocated_slots_count >= max_slots_to_allocate:
                ex_reason = ExclusionReasonCode.INSUFFICIENT_CAPACITY
            elif any(run.remaining_slots > 0 for run in slot_runs):
                ex_reason = ExclusionReasonCode.WINDOW_TOO_SMALL
            else:
                ex_reason = ExclusionReasonCode.INSUFFICIENT_CAPACITY

            unscheduled_records.append(
                ShortfallRecord(
                    task_id=task.id,
                    task_title=task.title,
                    unscheduled_minutes=task_remaining_effort[task.id],
                    reason_code=ex_reason,
                )
            )
        elif task_remaining_effort[task.id] > 0:
            # Partially scheduled
            ex_reason = (
                ExclusionReasonCode.MAX_DAILY_SPLITS_REACHED
                if task_splits_count[task.id] >= policy.max_daily_task_blocks
                else ExclusionReasonCode.INSUFFICIENT_CAPACITY
            )
            unscheduled_records.append(
                ShortfallRecord(
                    task_id=task.id,
                    task_title=task.title,
                    unscheduled_minutes=task_remaining_effort[task.id],
                    reason_code=ex_reason,
                )
            )

    # Sort schedule blocks chronologically by start_time
    schedule_blocks.sort(key=lambda b: time_to_minutes(b.start_time))

    total_allocated_minutes = sum(b.duration_minutes for b in schedule_blocks)
    total_shortfall_minutes = sum(r.unscheduled_minutes for r in unscheduled_records)

    shortfall_report = ShortfallReport(
        total_shortfall_minutes=total_shortfall_minutes,
        usable_capacity_minutes=usable_capacity_minutes,
        records=unscheduled_records,
    )

    return PlanningResult(
        user_id=user_id,
        plan_date=plan_date,
        usable_capacity_minutes=usable_capacity_minutes,
        allocated_minutes=total_allocated_minutes,
        buffer_minutes=buffer_minutes,
        shortfall_minutes=total_shortfall_minutes,
        blocks=schedule_blocks,
        shortfall_report=shortfall_report,
    )
