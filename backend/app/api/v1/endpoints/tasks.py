from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import TaskNotFoundException, GoalNotFoundException
from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.task.service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Create a new Task assigned to a specific Goal.
    Validates that the parent Goal exists.
    """
    try:
        return TaskService.create_task(db, task_in)
    except GoalNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.get("", response_model=List[TaskResponse])
def get_tasks(
    goal_id: Optional[int] = Query(None, description="Filter tasks by parent Goal ID"),
    status_filter: Optional[TaskStatus] = Query(None, alias="status", description="Filter tasks by status"),
    db: Session = Depends(get_db),
) -> List[TaskResponse]:
    """List Tasks, optionally filtered by goal_id or status."""
    return TaskService.get_tasks(db, goal_id=goal_id, status=status_filter)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
) -> TaskResponse:
    """Retrieve a specific Task by ID."""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Update attributes of an existing Task.
    Synchronizes completed_at timestamp when status transitions to/from COMPLETED.
    """
    try:
        return TaskService.update_task(db, task_id, task_in)
    except TaskNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a specific Task."""
    try:
        TaskService.delete_task(db, task_id)
    except TaskNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
