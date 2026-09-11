from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.goal import Goal
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate
from app.core.exceptions import TaskNotFoundException, GoalNotFoundException


class TaskService:
    @staticmethod
    def create_task(db: Session, task_in: TaskCreate) -> Task:
        """
        Create a new task under an existing Goal.
        Enforces strict Task -> Goal relationship.
        """
        parent_goal = db.query(Goal).filter(Goal.id == task_in.goal_id).first()
        if not parent_goal:
            raise GoalNotFoundException(f"Cannot create task: parent Goal with id {task_in.goal_id} does not exist")

        # Synchronize completed_at based on initial status
        completed_at = task_in.completed_at
        if task_in.status == TaskStatus.COMPLETED and completed_at is None:
            completed_at = datetime.now(timezone.utc)
        elif task_in.status != TaskStatus.COMPLETED:
            completed_at = None

        task = Task(
            goal_id=task_in.goal_id,
            title=task_in.title,
            description=task_in.description,
            status=task_in.status,
            priority=task_in.priority,
            estimated_minutes=task_in.estimated_minutes,
            deadline=task_in.deadline,
            completed_at=completed_at,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_tasks(
        db: Session,
        goal_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
    ) -> List[Task]:
        """List tasks, optionally filtered by goal_id or status."""
        query = db.query(Task)
        if goal_id is not None:
            query = query.filter(Task.goal_id == goal_id)
        if status is not None:
            query = query.filter(Task.status == status)
        return query.order_by(Task.created_at.asc()).all()

    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[Task]:
        """Fetch a single task by ID."""
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def update_task(db: Session, task_id: int, task_in: TaskUpdate) -> Task:
        """
        Update an existing task and maintain completed_at integrity.
        """
        task = TaskService.get_task(db, task_id)
        if not task:
            raise TaskNotFoundException(f"Task with id {task_id} not found")

        update_data = task_in.model_dump(exclude_unset=True)

        # Handle status transitions and completed_at timestamp
        if "status" in update_data:
            new_status = update_data["status"]
            if new_status == TaskStatus.COMPLETED:
                if "completed_at" not in update_data or update_data["completed_at"] is None:
                    update_data["completed_at"] = datetime.now(timezone.utc)
            else:
                # When moving away from COMPLETED, clear completed_at unless explicitly specified
                if "completed_at" not in update_data:
                    update_data["completed_at"] = None

        for field, value in update_data.items():
            setattr(task, field, value)

        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def complete_task(db: Session, task_id: int) -> Task:
        """Convenience method to transition a task to COMPLETED."""
        return TaskService.update_task(
            db,
            task_id,
            TaskUpdate(status=TaskStatus.COMPLETED),
        )

    @staticmethod
    def delete_task(db: Session, task_id: int) -> None:
        """Safely delete a single task."""
        task = TaskService.get_task(db, task_id)
        if not task:
            raise TaskNotFoundException(f"Task with id {task_id} not found")

        db.delete(task)
        db.commit()
