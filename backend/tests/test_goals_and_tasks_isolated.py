"""
Isolated Domain & API Tests for Goals + Tasks.
Runs in an isolated, in-memory test environment to rigorously validate business logic,
service rules, and API endpoints without requiring an active PostgreSQL database instance.
"""

from app.models.goal import GoalStatus, GoalPriority
from app.models.task import TaskStatus, TaskPriority


def test_1_create_goal(client):
    """1. Test creating a Goal via API endpoint."""
    payload = {
        "title": "Master Time Management",
        "description": "Establish proactive planning routines",
        "status": "ACTIVE",
        "priority": "HIGH",
    }
    response = client.post("/api/v1/goals", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Master Time Management"
    assert data["status"] == "ACTIVE"
    assert data["priority"] == "HIGH"
    assert data["user_id"] == 1


def test_2_read_goals(client):
    """2. Test reading Goals (list and single retrieval)."""
    # Create two goals
    client.post("/api/v1/goals", json={"title": "Goal Alpha", "priority": "LOW"})
    client.post("/api/v1/goals", json={"title": "Goal Beta", "priority": "HIGH"})

    # List goals
    response = client.get("/api/v1/goals")
    assert response.status_code == 200
    goals = response.json()
    assert len(goals) == 2

    # Get single goal by ID
    goal_id = goals[0]["id"]
    single_res = client.get(f"/api/v1/goals/{goal_id}")
    assert single_res.status_code == 200
    assert single_res.json()["id"] == goal_id


def test_3_update_goal(client):
    """3. Test updating a Goal."""
    create_res = client.post("/api/v1/goals", json={"title": "Initial Goal", "priority": "LOW"})
    goal_id = create_res.json()["id"]

    # Update title and priority
    update_res = client.patch(f"/api/v1/goals/{goal_id}", json={
        "title": "Updated Goal Title",
        "priority": "HIGH",
        "status": "COMPLETED",
    })
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["title"] == "Updated Goal Title"
    assert updated["priority"] == "HIGH"
    assert updated["status"] == "COMPLETED"


def test_4_create_task_under_goal(client):
    """4. Test creating a Task under a Goal."""
    # First create a goal
    goal_res = client.post("/api/v1/goals", json={"title": "Project Sprint", "priority": "HIGH"})
    goal_id = goal_res.json()["id"]

    # Create task assigned to this goal
    task_payload = {
        "goal_id": goal_id,
        "title": "Write unit tests",
        "description": "Comprehensive test coverage for M1",
        "priority": "HIGH",
        "estimated_minutes": 60,
    }
    task_res = client.post("/api/v1/tasks", json=task_payload)
    assert task_res.status_code == 201
    task = task_res.json()
    assert task["id"] is not None
    assert task["goal_id"] == goal_id
    assert task["title"] == "Write unit tests"
    assert task["status"] == "TODO"
    assert task["estimated_minutes"] == 60
    assert task["completed_at"] is None


def test_5_read_tasks(client):
    """5. Test reading Tasks and filtering by goal_id."""
    # Create Goal 1 and Goal 2
    g1 = client.post("/api/v1/goals", json={"title": "G1"}).json()["id"]
    g2 = client.post("/api/v1/goals", json={"title": "G2"}).json()["id"]

    client.post("/api/v1/tasks", json={"goal_id": g1, "title": "Task 1 for G1"})
    client.post("/api/v1/tasks", json={"goal_id": g1, "title": "Task 2 for G1"})
    client.post("/api/v1/tasks", json={"goal_id": g2, "title": "Task 1 for G2"})

    # All tasks
    all_res = client.get("/api/v1/tasks")
    assert all_res.status_code == 200
    assert len(all_res.json()) == 3

    # Filtered by G1
    g1_res = client.get(f"/api/v1/tasks?goal_id={g1}")
    assert g1_res.status_code == 200
    assert len(g1_res.json()) == 2
    for t in g1_res.json():
        assert t["goal_id"] == g1


def test_6_update_task(client):
    """6. Test updating a Task."""
    goal = client.post("/api/v1/goals", json={"title": "Goal"}).json()
    task = client.post("/api/v1/tasks", json={"goal_id": goal["id"], "title": "Draft spec"}).json()
    task_id = task["id"]

    update_res = client.patch(f"/api/v1/tasks/{task_id}", json={
        "title": "Draft finalized spec",
        "estimated_minutes": 90,
        "status": "IN_PROGRESS",
    })
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["title"] == "Draft finalized spec"
    assert updated["estimated_minutes"] == 90
    assert updated["status"] == "IN_PROGRESS"


def test_7_complete_task_sets_completed_at(client):
    """7. Test completing a Task sets completed_at correctly, and reverting clears it."""
    goal = client.post("/api/v1/goals", json={"title": "Goal"}).json()
    task = client.post("/api/v1/tasks", json={"goal_id": goal["id"], "title": "Review PR"}).json()
    task_id = task["id"]
    assert task["completed_at"] is None

    # Mark COMPLETED
    complete_res = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "COMPLETED"})
    assert complete_res.status_code == 200
    completed_task = complete_res.json()
    assert completed_task["status"] == "COMPLETED"
    assert completed_task["completed_at"] is not None

    # Revert back to IN_PROGRESS -> completed_at should be cleared
    revert_res = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "IN_PROGRESS"})
    assert revert_res.status_code == 200
    reverted_task = revert_res.json()
    assert reverted_task["status"] == "IN_PROGRESS"
    assert reverted_task["completed_at"] is None


def test_10_task_to_goal_relationship_respected(client):
    """10. Test that creating a Task under a nonexistent Goal is rejected."""
    bad_payload = {
        "goal_id": 99999,  # Nonexistent Goal ID
        "title": "Orphan task",
    }
    res = client.post("/api/v1/tasks", json=bad_payload)
    assert res.status_code == 404
    assert "does not exist" in res.json()["detail"]


def test_conservative_goal_deletion_behavior(client):
    """
    Verify conservative deletion:
    Deleting a Goal that still contains tasks must be rejected with 409 Conflict.
    """
    goal = client.post("/api/v1/goals", json={"title": "Important Goal"}).json()
    goal_id = goal["id"]
    task = client.post("/api/v1/tasks", json={"goal_id": goal_id, "title": "Subtask"}).json()
    task_id = task["id"]

    # Attempting to delete Goal while Task exists should be rejected (409)
    delete_goal_res = client.delete(f"/api/v1/goals/{goal_id}")
    assert delete_goal_res.status_code == 409
    assert "contains 1 task" in delete_goal_res.json()["detail"]

    # Delete the task first
    del_task_res = client.delete(f"/api/v1/tasks/{task_id}")
    assert del_task_res.status_code == 204

    # Now goal deletion succeeds
    delete_goal_res_2 = client.delete(f"/api/v1/goals/{goal_id}")
    assert delete_goal_res_2.status_code == 204

    # Verify goal is gone
    get_res = client.get(f"/api/v1/goals/{goal_id}")
    assert get_res.status_code == 404
