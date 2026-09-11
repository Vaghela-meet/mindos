import pytest
from pydantic import ValidationError
from app.models.goal import GoalStatus, GoalPriority
from app.models.task import TaskStatus, TaskPriority
from app.schemas.goal import GoalCreate, GoalUpdate
from app.schemas.task import TaskCreate, TaskUpdate


def test_goal_schema_valid():
    """Verify GoalCreate accepts valid data."""
    goal = GoalCreate(
        title="Ship MindOS M1",
        description="Deliver Goal and Task domain foundation",
        status=GoalStatus.ACTIVE,
        priority=GoalPriority.HIGH,
    )
    assert goal.title == "Ship MindOS M1"
    assert goal.status == GoalStatus.ACTIVE
    assert goal.priority == GoalPriority.HIGH


def test_goal_schema_rejects_empty_or_whitespace_title():
    """Verify GoalCreate rejects empty or whitespace-only titles."""
    with pytest.raises(ValidationError):
        GoalCreate(title="")

    with pytest.raises(ValidationError):
        GoalCreate(title="    ")


def test_goal_schema_rejects_invalid_enums():
    """Verify GoalCreate rejects invalid status or priority enums."""
    with pytest.raises(ValidationError):
        GoalCreate(title="Test", status="INVALID_STATUS")

    with pytest.raises(ValidationError):
        GoalCreate(title="Test", priority="SUPER_HIGH")


def test_task_schema_valid():
    """Verify TaskCreate accepts valid data."""
    task = TaskCreate(
        goal_id=1,
        title="Design database schema",
        estimated_minutes=45,
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.TODO,
    )
    assert task.goal_id == 1
    assert task.title == "Design database schema"
    assert task.estimated_minutes == 45


def test_task_schema_rejects_non_positive_estimated_minutes():
    """Verify TaskCreate rejects zero or negative estimated_minutes."""
    # Test zero
    with pytest.raises(ValidationError) as excinfo_zero:
        TaskCreate(goal_id=1, title="Test", estimated_minutes=0)
    assert "Estimated minutes must be strictly positive" in str(excinfo_zero.value)

    # Test negative
    with pytest.raises(ValidationError) as excinfo_neg:
        TaskCreate(goal_id=1, title="Test", estimated_minutes=-15)
    assert "Estimated minutes must be strictly positive" in str(excinfo_neg.value)


def test_task_update_rejects_invalid_estimated_minutes():
    """Verify TaskUpdate rejects non-positive estimated_minutes."""
    with pytest.raises(ValidationError):
        TaskUpdate(estimated_minutes=-5)

    with pytest.raises(ValidationError):
        TaskUpdate(estimated_minutes=0)


def test_task_schema_rejects_invalid_enums():
    """Verify TaskCreate rejects invalid status or priority enums."""
    with pytest.raises(ValidationError):
        TaskCreate(goal_id=1, title="Test", status="COMPLETING")

    with pytest.raises(ValidationError):
        TaskCreate(goal_id=1, title="Test", priority="URGENT")
