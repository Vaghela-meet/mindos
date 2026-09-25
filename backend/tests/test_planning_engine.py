import pytest
from datetime import date, time, datetime, timedelta
from app.models.task import Task, TaskStatus, TaskPriority, TaskType
from app.models.goal import Goal, GoalStatus, GoalPriority
from app.models.availability import Availability, DayOfWeek
from app.models.daily_plan import ScheduleReasonCode, ExclusionReasonCode
from app.schemas.plan import PlannerPolicy
from app.services.planning.engine import (
    generate_deterministic_daily_plan,
    build_slot_runs_from_availability,
)
from app.services.planning.sorter import candidate_sort_key


def create_mock_goal(goal_id: int, title: str, priority: GoalPriority = GoalPriority.MEDIUM) -> Goal:
    g = Goal(
        id=goal_id,
        user_id=1,
        title=title,
        status=GoalStatus.ACTIVE,
        priority=priority,
    )
    return g


def create_mock_task(
    task_id: int,
    goal_id: int,
    title: str,
    priority: TaskPriority = TaskPriority.MEDIUM,
    task_type: TaskType = TaskType.SHALLOW_WORK,
    estimated_minutes: int = 60,
    status: TaskStatus = TaskStatus.TODO,
    deadline: datetime = None,
    created_at: datetime = None,
) -> Task:
    t = Task(
        id=task_id,
        goal_id=goal_id,
        title=title,
        priority=priority,
        task_type=task_type,
        estimated_minutes=estimated_minutes,
        status=status,
        deadline=deadline,
        created_at=created_at or datetime(2026, 9, 1, 9, 0),
    )
    return t


def create_mock_window(
    win_id: int,
    day_of_week: DayOfWeek,
    start_time: time,
    end_time: time,
) -> Availability:
    return Availability(
        id=win_id,
        user_id=1,
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time,
    )


class TestPlanningEnginePure:
    """Pure algorithmic unit tests verifying M3 planning engine correctness."""

    def test_determinism_identical_runs(self):
        """Identical inputs must yield 100% identical outputs across 10 runs."""
        plan_date = date(2026, 9, 25)
        goal = create_mock_goal(1, "Core Platform", GoalPriority.HIGH)
        tasks = [
            create_mock_task(1, 1, "Task A", TaskPriority.HIGH, TaskType.DEEP_WORK, 90),
            create_mock_task(2, 1, "Task B", TaskPriority.MEDIUM, TaskType.SHALLOW_WORK, 60),
            create_mock_task(3, 1, "Task C", TaskPriority.LOW, TaskType.ADMINISTRATIVE, 30),
        ]
        windows = [
            create_mock_window(1, DayOfWeek.FRIDAY, time(9, 0), time(12, 0)),
            create_mock_window(2, DayOfWeek.FRIDAY, time(13, 0), time(16, 0)),
        ]

        runs_output = []
        for _ in range(10):
            res = generate_deterministic_daily_plan(
                user_id=1,
                plan_date=plan_date,
                user_timezone="UTC",
                availability_windows=windows,
                candidate_tasks=tasks,
                active_goals=[goal],
            )
            runs_output.append(
                (
                    [b.task_id for b in res.blocks],
                    [(b.start_time, b.end_time) for b in res.blocks],
                    [b.schedule_reason_code for b in res.blocks],
                    res.usable_capacity_minutes,
                    res.allocated_minutes,
                    res.shortfall_minutes,
                    [r.task_id for r in res.shortfall_report.records],
                )
            )

        first_run = runs_output[0]
        for run in runs_output[1:]:
            assert run == first_run, "Determinism violated across execution runs"

    def test_capacity_ceiling_and_15_percent_buffer(self):
        """
        Raw availability = 360m (6h).
        85% usable = 306m -> floored to 30m grid = 300m usable.
        Protected buffer = 360 - 300 = 60m.
        """
        plan_date = date(2026, 9, 25)
        goal = create_mock_goal(1, "Deep Focus", GoalPriority.HIGH)
        # Total candidate effort = 450m (exceeds 300m usable)
        tasks = [
            create_mock_task(i, 1, f"Task {i}", TaskPriority.HIGH, TaskType.SHALLOW_WORK, 60)
            for i in range(1, 8)
        ]
        windows = [
            create_mock_window(1, DayOfWeek.FRIDAY, time(9, 0), time(15, 0)),  # 6 hours = 360m
        ]

        res = generate_deterministic_daily_plan(
            user_id=1,
            plan_date=plan_date,
            user_timezone="UTC",
            availability_windows=windows,
            candidate_tasks=tasks,
            active_goals=[goal],
        )

        assert res.usable_capacity_minutes == 300
        assert res.buffer_minutes == 60
        assert res.allocated_minutes <= 300
        assert res.allocated_minutes == 300  # Packed up to usable capacity
        # Remainder is shortfall
        assert res.shortfall_minutes > 0
        assert res.shortfall_report.total_shortfall_minutes > 0

    def test_window_awareness_and_gap_preservation(self):
        """
        Two windows: Morning 09:00-12:00, Afternoon 14:00-17:00 (Lunch gap: 12:00-14:00).
        Blocks must NEVER span across the 12:00-14:00 gap.
        """
        plan_date = date(2026, 9, 25)
        goal = create_mock_goal(1, "Sprint Work", GoalPriority.HIGH)
        tasks = [
            create_mock_task(1, 1, "Morning Task", TaskPriority.HIGH, TaskType.DEEP_WORK, 120),
            create_mock_task(2, 1, "Afternoon Task", TaskPriority.MEDIUM, TaskType.SHALLOW_WORK, 90),
        ]
        windows = [
            create_mock_window(1, DayOfWeek.FRIDAY, time(9, 0), time(12, 0)),   # 180m
            create_mock_window(2, DayOfWeek.FRIDAY, time(14, 0), time(17, 0)),  # 180m
        ]

        res = generate_deterministic_daily_plan(
            user_id=1,
            plan_date=plan_date,
            user_timezone="UTC",
            availability_windows=windows,
            candidate_tasks=tasks,
            active_goals=[goal],
        )

        for b in res.blocks:
            # Block must be in 09:00-12:00 or 14:00-17:00
            is_morning = b.start_time >= time(9, 0) and b.end_time <= time(12, 0)
            is_afternoon = b.start_time >= time(14, 0) and b.end_time <= time(17, 0)
            assert is_morning or is_afternoon, f"Block {b.start_time}-{b.end_time} crossed inter-window gap"

    def test_adjacent_windows_merging(self):
        """
        Touching boundary windows (09:00-12:00 and 12:00-15:00) merge into one continuous run.
        A 180m task can cleanly schedule from 11:00 to 14:00.
        """
        windows = [
            create_mock_window(1, DayOfWeek.FRIDAY, time(9, 0), time(12, 0)),
            create_mock_window(2, DayOfWeek.FRIDAY, time(12, 0), time(15, 0)),
        ]
        runs = build_slot_runs_from_availability(windows, 30)
        assert len(runs) == 1
        assert runs[0].total_slots == 12  # 6 hours = 12 slots

    def test_task_splitting_policy_and_floor(self):
        """
        DEEP_WORK requires at least 60m. If only 30m remains in a window, it must NOT split into 30m.
        """
        policy = PlannerPolicy(
            usable_capacity_ratio=1.0,  # 100% for this test
            minimum_deep_work_block=60,
            minimum_standard_block=30,
            max_daily_task_blocks=2,
        )
        plan_date = date(2026, 9, 25)
        goal = create_mock_goal(1, "Deep Focus", GoalPriority.HIGH)
        tasks = [
            create_mock_task(1, 1, "Filler", TaskPriority.HIGH, TaskType.SHALLOW_WORK, 90),
            create_mock_task(2, 1, "Deep Work", TaskPriority.MEDIUM, TaskType.DEEP_WORK, 90),
        ]
        # Window 1 has 120m (09:00-11:00). Filler takes 90m (09:00-10:30), leaving 30m (10:30-11:00).
        # Deep Work needs 60m min, so it cannot take the 30m residual; it must go to Window 2.
        windows = [
            create_mock_window(1, DayOfWeek.FRIDAY, time(9, 0), time(11, 0)),   # 120m
            create_mock_window(2, DayOfWeek.FRIDAY, time(13, 0), time(16, 0)),  # 180m
        ]

        res = generate_deterministic_daily_plan(
            user_id=1,
            plan_date=plan_date,
            user_timezone="UTC",
            availability_windows=windows,
            candidate_tasks=tasks,
            active_goals=[goal],
            policy=policy,
        )

        deep_blocks = [b for b in res.blocks if b.task_id == 2]
        for db in deep_blocks:
            assert db.duration_minutes >= 60, f"Deep work block was split below 60m floor: {db.duration_minutes}m"

    def test_deadline_pressure_overrides_priority(self):
        """
        Low priority task with imminent deadline overrides High priority task with distant deadline.
        """
        plan_date = date(2026, 9, 25)
        goal = create_mock_goal(1, "Ops", GoalPriority.MEDIUM)
        urgent_task = create_mock_task(
            task_id=1,
            goal_id=1,
            title="Urgent Low Prio",
            priority=TaskPriority.LOW,
            deadline=datetime(2026, 9, 25, 17, 0),  # Due today!
            estimated_minutes=60,
        )
        distant_task = create_mock_task(
            task_id=2,
            goal_id=1,
            title="Distant High Prio",
            priority=TaskPriority.HIGH,
            deadline=datetime(2026, 10, 15, 17, 0),  # Due 20 days later
            estimated_minutes=60,
        )
        windows = [
            create_mock_window(1, DayOfWeek.FRIDAY, time(9, 0), time(11, 0)),
        ]

        res = generate_deterministic_daily_plan(
            user_id=1,
            plan_date=plan_date,
            user_timezone="UTC",
            availability_windows=windows,
            candidate_tasks=[distant_task, urgent_task],
            active_goals=[goal],
        )

        assert len(res.blocks) >= 1
        # Urgent task scheduled first at 09:00
        assert res.blocks[0].task_id == 1
        assert res.blocks[0].schedule_reason_code == ScheduleReasonCode.DEADLINE_PRESSURE_IMMINENT

    def test_empty_availability_day(self):
        """Zero availability day returns clean empty plan with NO_AVAILABILITY code."""
        plan_date = date(2026, 9, 25)
        goal = create_mock_goal(1, "Goal", GoalPriority.HIGH)
        tasks = [create_mock_task(1, 1, "Task A", TaskPriority.HIGH, TaskType.SHALLOW_WORK, 60)]

        res = generate_deterministic_daily_plan(
            user_id=1,
            plan_date=plan_date,
            user_timezone="UTC",
            availability_windows=[],  # No windows
            candidate_tasks=tasks,
            active_goals=[goal],
        )

        assert res.usable_capacity_minutes == 0
        assert res.allocated_minutes == 0
        assert len(res.blocks) == 0
        assert res.shortfall_report is not None
        assert res.shortfall_report.records[0].reason_code == ExclusionReasonCode.NO_AVAILABILITY

    def test_empty_candidate_tasks(self):
        """No actionable candidate tasks returns clean empty plan with 0 allocated and 0 shortfall."""
        plan_date = date(2026, 9, 25)
        windows = [create_mock_window(1, DayOfWeek.FRIDAY, time(9, 0), time(12, 0))]

        res = generate_deterministic_daily_plan(
            user_id=1,
            plan_date=plan_date,
            user_timezone="UTC",
            availability_windows=windows,
            candidate_tasks=[],
            active_goals=[],
        )

        assert res.allocated_minutes == 0
        assert len(res.blocks) == 0
        assert res.shortfall_minutes == 0
        assert len(res.shortfall_report.records) == 0
