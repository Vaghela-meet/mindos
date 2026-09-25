from datetime import date, datetime
from typing import Optional
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user_id, ensure_dev_user
from app.core.exceptions import (
    PlanNotFoundException,
    PlanInvariantViolationException,
    PlanningValidationException,
)
from app.models.daily_plan import DailyPlan
from app.schemas.plan import (
    DailyPlanResponse,
    ScheduleBlockResponse,
    PlanGenerationRequest,
)
from app.services.planning.service import PlanService

router = APIRouter(prefix="/plans", tags=["Plans"])


def to_plan_response(plan: DailyPlan) -> DailyPlanResponse:
    block_responses = []
    for b in plan.blocks:
        task_title = b.task.title if b.task else None
        task_type = b.task.task_type if b.task else None
        goal_title = b.task.goal.title if (b.task and b.task.goal) else None
        goal_id = b.task.goal_id if b.task else None

        block_responses.append(
            ScheduleBlockResponse(
                id=b.id,
                plan_id=b.plan_id,
                task_id=b.task_id,
                start_time=b.start_time,
                end_time=b.end_time,
                duration_minutes=b.duration_minutes,
                status=b.status,
                schedule_reason_code=b.schedule_reason_code,
                task_title=task_title,
                task_type=task_type,
                goal_title=goal_title,
                goal_id=goal_id,
                created_at=b.created_at,
                updated_at=b.updated_at,
            )
        )

    shortfall_report = getattr(plan, "shortfall_report", None)

    return DailyPlanResponse(
        id=plan.id,
        user_id=plan.user_id,
        plan_date=plan.plan_date,
        status=plan.status,
        usable_capacity_minutes=plan.usable_capacity_minutes,
        allocated_minutes=plan.allocated_minutes,
        buffer_minutes=plan.buffer_minutes,
        shortfall_minutes=plan.shortfall_minutes,
        notes=plan.notes,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        blocks=block_responses,
        shortfall_report=shortfall_report,
    )


@router.post("/generate", response_model=DailyPlanResponse, status_code=status.HTTP_201_CREATED)
def generate_plan(
    request: Optional[PlanGenerationRequest] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> DailyPlanResponse:
    """
    Generates and activates a deterministic daily plan for the specified date (defaults to today).
    Supersedes any existing active plan for that user and date.
    """
    user = ensure_dev_user(db, current_user_id)

    target_date = request.plan_date if (request and request.plan_date) else None
    if not target_date:
        # Determine today in user timezone
        try:
            tz = ZoneInfo(user.timezone) if user.timezone else ZoneInfo("UTC")
            target_date = datetime.now(tz).date()
        except Exception:
            target_date = datetime.now(ZoneInfo("UTC")).date()

    policy = request.policy if request else None

    try:
        plan = PlanService.generate_and_save_daily_plan(
            db=db,
            user_id=current_user_id,
            plan_date=target_date,
            policy=policy,
        )
        return to_plan_response(plan)
    except PlanInvariantViolationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
    except PlanningValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/today", response_model=DailyPlanResponse)
def get_today_plan(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> DailyPlanResponse:
    """
    Retrieves the active daily plan for today in the user's localized timezone.
    """
    user = ensure_dev_user(db, current_user_id)
    try:
        tz = ZoneInfo(user.timezone) if user.timezone else ZoneInfo("UTC")
        today_date = datetime.now(tz).date()
    except Exception:
        today_date = datetime.now(ZoneInfo("UTC")).date()

    plan = PlanService.get_active_plan_for_date(db, current_user_id, today_date)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active plan found for today ({today_date})",
        )
    return to_plan_response(plan)


@router.get("/daily/{plan_date}", response_model=DailyPlanResponse)
def get_daily_plan(
    plan_date: date,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> DailyPlanResponse:
    """
    Retrieves the active daily plan for the specified calendar date.
    """
    plan = PlanService.get_active_plan_for_date(db, current_user_id, plan_date)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active plan found for date {plan_date}",
        )
    return to_plan_response(plan)


@router.get("/{plan_id}", response_model=DailyPlanResponse)
def get_plan_by_id(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> DailyPlanResponse:
    """
    Retrieves a daily plan by its ID.
    """
    try:
        plan = PlanService.get_plan_by_id(db, plan_id, user_id=current_user_id)
        return to_plan_response(plan)
    except PlanNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
