from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.goal import Goal, GoalStatus
from app.models.task import Task
from app.schemas.goal import GoalCreate, GoalUpdate
from app.core.exceptions import GoalNotFoundException, GoalHasActiveTasksException
from app.core.deps import ensure_dev_user


class GoalService:
    @staticmethod
    def create_goal(db: Session, goal_in: GoalCreate, user_id: int) -> Goal:
        """Create a new goal for the specified user."""
        ensure_dev_user(db, user_id)

        goal = Goal(
            user_id=user_id,
            title=goal_in.title,
            description=goal_in.description,
            status=goal_in.status,
            priority=goal_in.priority,
            deadline=goal_in.deadline,
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def get_goals(
        db: Session,
        user_id: int,
        status: Optional[GoalStatus] = None,
    ) -> List[Goal]:
        """List goals belonging to a user, optionally filtered by status."""
        query = db.query(Goal).filter(Goal.user_id == user_id)
        if status is not None:
            query = query.filter(Goal.status == status)
        return query.order_by(Goal.created_at.desc()).all()

    @staticmethod
    def get_goal(
        db: Session,
        goal_id: int,
        user_id: Optional[int] = None,
    ) -> Optional[Goal]:
        """Fetch a single goal by ID."""
        query = db.query(Goal).filter(Goal.id == goal_id)
        if user_id is not None:
            query = query.filter(Goal.user_id == user_id)
        return query.first()

    @staticmethod
    def update_goal(
        db: Session,
        goal_id: int,
        goal_in: GoalUpdate,
        user_id: Optional[int] = None,
    ) -> Goal:
        """Update existing goal attributes."""
        goal = GoalService.get_goal(db, goal_id, user_id)
        if not goal:
            raise GoalNotFoundException(f"Goal with id {goal_id} not found")

        update_data = goal_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)

        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def delete_goal(
        db: Session,
        goal_id: int,
        user_id: Optional[int] = None,
    ) -> None:
        """
        Conservative deletion:
        Rejects deletion if any tasks remain associated with this goal to prevent accidental data loss.
        """
        goal = GoalService.get_goal(db, goal_id, user_id)
        if not goal:
            raise GoalNotFoundException(f"Goal with id {goal_id} not found")

        # Check for existing tasks
        task_count = db.query(Task).filter(Task.goal_id == goal_id).count()
        if task_count > 0:
            raise GoalHasActiveTasksException(
                f"Cannot delete goal '{goal.title}' because it contains {task_count} task(s). "
                "Archive the goal or remove/reassign its tasks first to prevent accidental data loss."
            )

        db.delete(goal)
        db.commit()
