from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user_id
from app.core.exceptions import GoalNotFoundException, GoalHasActiveTasksException
from app.models.goal import GoalStatus
from app.schemas.goal import GoalCreate, GoalUpdate, GoalResponse
from app.services.goal.service import GoalService

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal_in: GoalCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> GoalResponse:
    """Create a new Goal for the active user."""
    return GoalService.create_goal(db, goal_in, current_user_id)


@router.get("", response_model=List[GoalResponse])
def get_goals(
    status_filter: Optional[GoalStatus] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> List[GoalResponse]:
    """List all Goals belonging to the active user, with optional status filter."""
    return GoalService.get_goals(db, current_user_id, status=status_filter)


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> GoalResponse:
    """Retrieve a specific Goal by ID."""
    goal = GoalService.get_goal(db, goal_id, user_id=current_user_id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id {goal_id} not found",
        )
    return goal


@router.patch("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: int,
    goal_in: GoalUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> GoalResponse:
    """Update attributes of an existing Goal."""
    try:
        return GoalService.update_goal(db, goal_id, goal_in, user_id=current_user_id)
    except GoalNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> None:
    """
    Delete a Goal.
    Enforces conservative deletion: blocked if active tasks exist to prevent accidental data loss.
    """
    try:
        GoalService.delete_goal(db, goal_id, user_id=current_user_id)
    except GoalNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except GoalHasActiveTasksException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
