from datetime import date, datetime
from typing import Optional, Tuple, Any
from app.models.task import Task, TaskPriority, TaskStatus, TaskType
from app.models.goal import Goal, GoalPriority
from app.models.daily_plan import ScheduleReasonCode


def get_importance_tier(task_priority: TaskPriority, goal_priority: Optional[GoalPriority]) -> int:
    """
    Computes deterministic importance tier (1 through 6) based on Goal Priority x Task Priority matrix.
    """
    g_prio = goal_priority or GoalPriority.MEDIUM

    if g_prio == GoalPriority.HIGH and task_priority == TaskPriority.HIGH:
        return 1
    elif (g_prio == GoalPriority.HIGH and task_priority == TaskPriority.MEDIUM) or \
         (g_prio == GoalPriority.MEDIUM and task_priority == TaskPriority.HIGH):
        return 2
    elif (g_prio == GoalPriority.HIGH and task_priority == TaskPriority.LOW) or \
         (g_prio == GoalPriority.LOW and task_priority == TaskPriority.HIGH):
        return 3
    elif g_prio == GoalPriority.MEDIUM and task_priority == TaskPriority.MEDIUM:
        return 4
    elif (g_prio == GoalPriority.MEDIUM and task_priority == TaskPriority.LOW) or \
         (g_prio == GoalPriority.LOW and task_priority == TaskPriority.MEDIUM):
        return 5
    else:  # LOW x LOW
        return 6


def get_urgency_info(task: Task, planning_date: date) -> Tuple[int, float]:
    """
    Computes (urgency_tier, sortable_deadline_timestamp) relative to planning_date:
    0: Overdue (delta < 0)
    1: Imminent (0 <= delta <= 1)
    2: Approaching (2 <= delta <= 7)
    3: Distant (delta > 7)
    4: No deadline
    """
    if not task.deadline:
        return (4, float("inf"))

    deadline_date = task.deadline.date() if isinstance(task.deadline, datetime) else task.deadline
    delta_days = (deadline_date - planning_date).days

    timestamp = task.deadline.timestamp() if isinstance(task.deadline, datetime) else datetime.combine(task.deadline, datetime.min.time()).timestamp()

    if delta_days < 0:
        return (0, timestamp)
    elif delta_days <= 1:
        return (1, timestamp)
    elif delta_days <= 7:
        return (2, timestamp)
    else:
        return (3, timestamp)


def candidate_sort_key(
    task: Task,
    goal: Optional[Goal],
    planning_date: date,
    last_goal_id: Optional[int] = None,
    last_task_type: Optional[TaskType] = None,
) -> Tuple[Any, ...]:
    """
    Stable deterministic lexicographic sorting key.
    Tie-breaking hierarchy:
    1. Urgency Tier (0=Overdue, 1=Imminent, 2=Approaching, 3=Distant, 4=None)
    2. Earlier Deadline Timestamp
    3. Importance Tier (1 to 6)
    4. Task Priority (HIGH=0, MEDIUM=1, LOW=2)
    5. Goal Priority (HIGH=0, MEDIUM=1, LOW=2)
    6. Context Continuity (0 if matches preceding block goal/type, else 1)
    7. Task State (IN_PROGRESS=0, TODO=1)
    8. Task Creation (created_at ascending)
    9. Entity ID (Task.id ascending)
    """
    urgency_tier, deadline_ts = get_urgency_info(task, planning_date)
    importance_tier = get_importance_tier(task.priority, goal.priority if goal else None)

    task_prio_val = {TaskPriority.HIGH: 0, TaskPriority.MEDIUM: 1, TaskPriority.LOW: 2}.get(task.priority, 1)
    goal_prio_val = {GoalPriority.HIGH: 0, GoalPriority.MEDIUM: 1, GoalPriority.LOW: 2}.get(goal.priority, 1) if goal else 1

    continuity_val = 0 if (last_goal_id is not None and task.goal_id == last_goal_id) else 1
    state_val = 0 if task.status == TaskStatus.IN_PROGRESS else 1
    created_val = task.created_at.timestamp() if task.created_at else 0.0

    return (
        urgency_tier,
        deadline_ts,
        importance_tier,
        task_prio_val,
        goal_prio_val,
        continuity_val,
        state_val,
        created_val,
        task.id,
    )


def determine_schedule_reason(
    task: Task,
    goal: Optional[Goal],
    planning_date: date,
    is_split: bool = False,
    is_continuity: bool = False,
    is_gap_fill: bool = False,
) -> ScheduleReasonCode:
    """
    Determines the primary explainable reason code for scheduling a block.
    """
    if is_split:
        return ScheduleReasonCode.PARTIAL_WINDOW_SPLIT

    urgency_tier, _ = get_urgency_info(task, planning_date)
    if urgency_tier == 0:
        return ScheduleReasonCode.DEADLINE_PRESSURE_OVERDUE
    if urgency_tier == 1:
        return ScheduleReasonCode.DEADLINE_PRESSURE_IMMINENT
    if urgency_tier == 2:
        return ScheduleReasonCode.DEADLINE_PRESSURE_APPROACHING

    if task.status == TaskStatus.IN_PROGRESS:
        return ScheduleReasonCode.TASK_IN_PROGRESS

    if is_continuity:
        return ScheduleReasonCode.CONTEXT_CONTINUITY

    if task.priority == TaskPriority.HIGH:
        return ScheduleReasonCode.TASK_PRIORITY_HIGH

    if goal and goal.priority == GoalPriority.HIGH:
        return ScheduleReasonCode.GOAL_ALIGNMENT_HIGH

    if is_gap_fill:
        return ScheduleReasonCode.GAP_FILL_ROUTINE

    return ScheduleReasonCode.PRIMARY_FIT
