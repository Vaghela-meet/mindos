import pytest
from datetime import date, time, datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.goal import Goal, GoalStatus, GoalPriority
from app.models.task import Task, TaskStatus, TaskPriority, TaskType
from app.models.availability import Availability, DayOfWeek
from app.models.daily_plan import DailyPlan, PlanStatus


def setup_test_data(db: Session, target_date: date) -> tuple[int, int]:
    """Helper to populate user, goal, tasks, and availability for target_date."""
    # Ensure User 1
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        user = User(id=1, email="test@example.com", name="Test User", timezone="UTC")
        db.add(user)
        db.commit()

    # Map target_date weekday
    weekday_map = {
        0: DayOfWeek.MONDAY,
        1: DayOfWeek.TUESDAY,
        2: DayOfWeek.WEDNESDAY,
        3: DayOfWeek.THURSDAY,
        4: DayOfWeek.FRIDAY,
        5: DayOfWeek.SATURDAY,
        6: DayOfWeek.SUNDAY,
    }
    dow = weekday_map[target_date.weekday()]

    # Clear prior data
    db.query(Availability).filter(Availability.user_id == 1).delete()
    db.query(Task).filter(Task.goal_id.in_([1, 2])).delete()
    db.query(Goal).filter(Goal.user_id == 1).delete()
    db.query(DailyPlan).filter(DailyPlan.user_id == 1).delete()
    db.commit()

    # Availability: 09:00 - 15:00 (6 hours = 360m -> 300m usable, 60m buffer)
    avail = Availability(
        user_id=1,
        day_of_week=dow,
        start_time=time(9, 0),
        end_time=time(15, 0),
    )
    db.add(avail)

    # Goal
    goal = Goal(
        id=1,
        user_id=1,
        title="MindOS Architecture",
        status=GoalStatus.ACTIVE,
        priority=GoalPriority.HIGH,
    )
    db.add(goal)
    db.commit()

    # Tasks
    t1 = Task(
        id=1,
        goal_id=1,
        title="Implement Planning Engine",
        status=TaskStatus.TODO,
        priority=TaskPriority.HIGH,
        task_type=TaskType.DEEP_WORK,
        estimated_minutes=90,
    )
    t2 = Task(
        id=2,
        goal_id=1,
        title="Review Invariant Assertions",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        task_type=TaskType.SHALLOW_WORK,
        estimated_minutes=60,
    )
    db.add_all([t1, t2])
    db.commit()

    return user.id, goal.id


class TestPlansAPI:
    """Verifies FastAPI REST endpoints for M3 daily planning."""

    def test_generate_plan_success(self, client: TestClient, db_session: Session):
        target_date = date(2026, 9, 25)
        setup_test_data(db_session, target_date)

        response = client.post(
            "/api/v1/plans/generate",
            json={"plan_date": target_date.isoformat()},
        )
        assert response.status_code == 201
        data = response.json()

        assert data["user_id"] == 1
        assert data["plan_date"] == target_date.isoformat()
        assert data["status"] == "ACTIVE"
        assert data["usable_capacity_minutes"] == 300
        assert data["allocated_minutes"] == 150  # 90m + 60m
        assert data["buffer_minutes"] == 60
        assert len(data["blocks"]) == 2

        # Check block attributes
        b1 = data["blocks"][0]
        assert b1["task_id"] == 1
        assert b1["task_title"] == "Implement Planning Engine"
        assert b1["task_type"] == "DEEP_WORK"
        assert b1["duration_minutes"] == 90
        assert b1["start_time"] == "09:00:00"
        assert b1["end_time"] == "10:30:00"

        b2 = data["blocks"][1]
        assert b2["task_id"] == 2
        assert b2["duration_minutes"] == 60
        assert b2["start_time"] == "10:30:00"
        assert b2["end_time"] == "11:30:00"

    def test_regenerate_plan_supersedes_previous(self, client: TestClient, db_session: Session):
        target_date = date(2026, 9, 25)
        setup_test_data(db_session, target_date)

        # First generation
        res1 = client.post(
            "/api/v1/plans/generate",
            json={"plan_date": target_date.isoformat()},
        )
        assert res1.status_code == 201
        plan1_id = res1.json()["id"]

        # Second generation (e.g. replanning)
        res2 = client.post(
            "/api/v1/plans/generate",
            json={"plan_date": target_date.isoformat()},
        )
        assert res2.status_code == 201
        plan2_id = res2.json()["id"]
        assert plan1_id != plan2_id

        # Verify plan 1 is now SUPERSEDED
        p1 = db_session.query(DailyPlan).filter(DailyPlan.id == plan1_id).first()
        assert p1.status == PlanStatus.SUPERSEDED

        # Verify plan 2 is ACTIVE
        p2 = db_session.query(DailyPlan).filter(DailyPlan.id == plan2_id).first()
        assert p2.status == PlanStatus.ACTIVE

    def test_get_daily_plan_by_date(self, client: TestClient, db_session: Session):
        target_date = date(2026, 9, 25)
        setup_test_data(db_session, target_date)

        # Before generation -> 404
        res = client.get(f"/api/v1/plans/daily/{target_date.isoformat()}")
        assert res.status_code == 404

        # Generate
        client.post(
            "/api/v1/plans/generate",
            json={"plan_date": target_date.isoformat()},
        )

        # Query again -> 200 OK
        res = client.get(f"/api/v1/plans/daily/{target_date.isoformat()}")
        assert res.status_code == 200
        assert res.json()["plan_date"] == target_date.isoformat()
        assert res.json()["status"] == "ACTIVE"

    def test_get_plan_by_id(self, client: TestClient, db_session: Session):
        target_date = date(2026, 9, 25)
        setup_test_data(db_session, target_date)

        gen_res = client.post(
            "/api/v1/plans/generate",
            json={"plan_date": target_date.isoformat()},
        )
        plan_id = gen_res.json()["id"]

        res = client.get(f"/api/v1/plans/{plan_id}")
        assert res.status_code == 200
        assert res.json()["id"] == plan_id

        # Non-existent ID -> 404
        missing_res = client.get("/api/v1/plans/999999")
        assert missing_res.status_code == 404
