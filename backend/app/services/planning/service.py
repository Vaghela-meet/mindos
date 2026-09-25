from datetime import date
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.core.exceptions import PlanNotFoundException
from app.models.user import User
from app.models.goal import Goal, GoalStatus
from app.models.task import Task, TaskStatus
from app.models.availability import Availability, DayOfWeek
from app.models.daily_plan import DailyPlan, ScheduleBlock, PlanStatus
from app.schemas.plan import PlannerPolicy
from app.services.planning.engine import generate_deterministic_daily_plan
from app.services.planning.invariants import validate_plan_invariants


WEEKDAY_MAP = {
    0: DayOfWeek.MONDAY,
    1: DayOfWeek.TUESDAY,
    2: DayOfWeek.WEDNESDAY,
    3: DayOfWeek.THURSDAY,
    4: DayOfWeek.FRIDAY,
    5: DayOfWeek.SATURDAY,
    6: DayOfWeek.SUNDAY,
}


class PlanService:
    """
    Coordinates plan generation, invariant validation, and transactional persistence.
    """

    @staticmethod
    def generate_and_save_daily_plan(
        db: Session,
        user_id: int,
        plan_date: date,
        policy: Optional[PlannerPolicy] = None,
    ) -> DailyPlan:
        """
        Generates a new deterministic daily plan, validates invariants, supersedes
        any existing active plan for that date, and persists the new plan and blocks atomically.
        """
        # Fetch user
        user = db.query(User).filter(User.id == user_id).first()
        user_timezone = user.timezone if user else "UTC"

        # Map weekday to DayOfWeek enum
        weekday_enum = WEEKDAY_MAP[plan_date.weekday()]

        # 1. Fetch user's availability windows for target weekday
        availability_windows = (
            db.query(Availability)
            .filter(Availability.user_id == user_id, Availability.day_of_week == weekday_enum)
            .all()
        )

        # 2. Fetch active goals
        active_goals = (
            db.query(Goal)
            .filter(Goal.user_id == user_id, Goal.status == GoalStatus.ACTIVE)
            .all()
        )
        active_goal_ids = [g.id for g in active_goals]

        # 3. Fetch candidate actionable tasks
        candidate_tasks = (
            db.query(Task)
            .filter(
                Task.goal_id.in_(active_goal_ids) if active_goal_ids else False,
                Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS]),
            )
            .all()
            if active_goal_ids
            else []
        )

        # 4. Run pure deterministic planning engine
        result = generate_deterministic_daily_plan(
            user_id=user_id,
            plan_date=plan_date,
            user_timezone=user_timezone,
            availability_windows=availability_windows,
            candidate_tasks=candidate_tasks,
            active_goals=active_goals,
            policy=policy,
        )

        # 5. Invariant validation
        validate_plan_invariants(
            user_id=user_id,
            usable_capacity_minutes=result.usable_capacity_minutes,
            blocks=result.blocks,
            availability_windows=availability_windows,
            candidate_tasks=candidate_tasks,
        )

        # 6. Transactional Persistence
        # Supersede any existing active plan for this date
        existing_active_plans = (
            db.query(DailyPlan)
            .filter(
                DailyPlan.user_id == user_id,
                DailyPlan.plan_date == plan_date,
                DailyPlan.status == PlanStatus.ACTIVE,
            )
            .all()
        )
        for ep in existing_active_plans:
            ep.status = PlanStatus.SUPERSEDED

        # Create new active DailyPlan
        new_plan = DailyPlan(
            user_id=user_id,
            plan_date=plan_date,
            status=PlanStatus.ACTIVE,
            usable_capacity_minutes=result.usable_capacity_minutes,
            allocated_minutes=result.allocated_minutes,
            buffer_minutes=result.buffer_minutes,
            shortfall_minutes=result.shortfall_minutes,
        )
        db.add(new_plan)
        db.flush()  # Populates new_plan.id

        # Create ScheduleBlock records
        for b in result.blocks:
            block_entity = ScheduleBlock(
                plan_id=new_plan.id,
                task_id=b.task_id,
                start_time=b.start_time,
                end_time=b.end_time,
                duration_minutes=b.duration_minutes,
                status=b.status,
                schedule_reason_code=b.schedule_reason_code,
            )
            db.add(block_entity)

        db.commit()
        db.refresh(new_plan)

        # Load blocks with task and goal details
        new_plan = (
            db.query(DailyPlan)
            .options(
                joinedload(DailyPlan.blocks).joinedload(ScheduleBlock.task).joinedload(Task.goal)
            )
            .filter(DailyPlan.id == new_plan.id)
            .first()
        )

        # Attach in-memory shortfall report for serializing
        new_plan.shortfall_report = result.shortfall_report

        return new_plan

    @staticmethod
    def get_active_plan_for_date(db: Session, user_id: int, plan_date: date) -> Optional[DailyPlan]:
        """
        Retrieves the active DailyPlan for the specified user and date, with eagerly loaded blocks and tasks.
        """
        return (
            db.query(DailyPlan)
            .options(
                joinedload(DailyPlan.blocks).joinedload(ScheduleBlock.task).joinedload(Task.goal)
            )
            .filter(
                DailyPlan.user_id == user_id,
                DailyPlan.plan_date == plan_date,
                DailyPlan.status == PlanStatus.ACTIVE,
            )
            .first()
        )

    @staticmethod
    def get_plan_by_id(db: Session, plan_id: int, user_id: Optional[int] = None) -> DailyPlan:
        """
        Retrieves a DailyPlan by ID, ensuring user scoping if user_id is provided.
        """
        query = (
            db.query(DailyPlan)
            .options(
                joinedload(DailyPlan.blocks).joinedload(ScheduleBlock.task).joinedload(Task.goal)
            )
            .filter(DailyPlan.id == plan_id)
        )
        if user_id is not None:
            query = query.filter(DailyPlan.user_id == user_id)

        plan = query.first()
        if not plan:
            raise PlanNotFoundException(f"DailyPlan with id {plan_id} not found")
        return plan
