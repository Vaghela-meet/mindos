"""
Isolated Domain & API Tests for Availability (M2).
Validates business logic, service rules, overlap rejection, adjacent window support,
ordering, and user scoping without requiring a live PostgreSQL daemon.
"""

import pytest
from app.models.availability import DayOfWeek


def test_create_valid_availability(client):
    """Verify creating a valid availability window returns 201."""
    payload = {
        "day_of_week": "MONDAY",
        "start_time": "09:00:00",
        "end_time": "12:00:00",
    }
    response = client.post("/api/v1/availability", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["day_of_week"] == "MONDAY"
    assert data["start_time"] == "09:00:00"
    assert data["end_time"] == "12:00:00"
    assert data["user_id"] == 1


def test_rejects_invalid_weekday(client):
    """Verify invalid weekday enum is rejected with 422."""
    payload = {
        "day_of_week": "FUNDAY",
        "start_time": "09:00:00",
        "end_time": "12:00:00",
    }
    response = client.post("/api/v1/availability", json=payload)
    assert response.status_code == 422


def test_rejects_inverted_start_end_time(client):
    """Verify start_time > end_time is rejected."""
    payload = {
        "day_of_week": "MONDAY",
        "start_time": "15:00:00",
        "end_time": "12:00:00",
    }
    response = client.post("/api/v1/availability", json=payload)
    assert response.status_code in [400, 422]


def test_rejects_equal_start_end_time(client):
    """Verify zero duration (start_time == end_time) is rejected."""
    payload = {
        "day_of_week": "MONDAY",
        "start_time": "10:00:00",
        "end_time": "10:00:00",
    }
    response = client.post("/api/v1/availability", json=payload)
    assert response.status_code in [400, 422]


def test_rejects_overlapping_windows(client):
    """Verify overlapping windows on the same weekday for the same user are rejected with 409 Conflict."""
    # 1. Base window: Monday 09:00 - 13:00
    res1 = client.post("/api/v1/availability", json={
        "day_of_week": "MONDAY",
        "start_time": "09:00:00",
        "end_time": "13:00:00",
    })
    assert res1.status_code == 201

    # 2. Overlap right: Monday 12:00 - 15:00
    res2 = client.post("/api/v1/availability", json={
        "day_of_week": "MONDAY",
        "start_time": "12:00:00",
        "end_time": "15:00:00",
    })
    assert res2.status_code == 409
    assert "overlaps with existing" in res2.json()["detail"]

    # 3. Overlap left: Monday 08:00 - 10:00
    res3 = client.post("/api/v1/availability", json={
        "day_of_week": "MONDAY",
        "start_time": "08:00:00",
        "end_time": "10:00:00",
    })
    assert res3.status_code == 409

    # 4. Enclosed: Monday 10:00 - 12:00
    res4 = client.post("/api/v1/availability", json={
        "day_of_week": "MONDAY",
        "start_time": "10:00:00",
        "end_time": "12:00:00",
    })
    assert res4.status_code == 409

    # 5. Enclosing: Monday 08:00 - 14:00
    res5 = client.post("/api/v1/availability", json={
        "day_of_week": "MONDAY",
        "start_time": "08:00:00",
        "end_time": "14:00:00",
    })
    assert res5.status_code == 409


def test_allows_adjacent_non_overlapping_windows(client):
    """Verify adjacent windows touching at boundary points (e.g. 09-12 and 12-15) are valid."""
    res1 = client.post("/api/v1/availability", json={
        "day_of_week": "MONDAY",
        "start_time": "09:00:00",
        "end_time": "12:00:00",
    })
    assert res1.status_code == 201

    # Adjacent after: 12:00 - 15:00
    res2 = client.post("/api/v1/availability", json={
        "day_of_week": "MONDAY",
        "start_time": "12:00:00",
        "end_time": "15:00:00",
    })
    assert res2.status_code == 201

    # Adjacent before: 06:00 - 09:00
    res3 = client.post("/api/v1/availability", json={
        "day_of_week": "MONDAY",
        "start_time": "06:00:00",
        "end_time": "09:00:00",
    })
    assert res3.status_code == 201


def test_allows_multiple_windows_on_same_weekday(client):
    """Verify multiple non-overlapping windows on the same weekday (e.g. 09-12 and 14-18) succeed."""
    res1 = client.post("/api/v1/availability", json={
        "day_of_week": "MONDAY",
        "start_time": "09:00:00",
        "end_time": "12:00:00",
    })
    assert res1.status_code == 201

    res2 = client.post("/api/v1/availability", json={
        "day_of_week": "MONDAY",
        "start_time": "14:00:00",
        "end_time": "18:00:00",
    })
    assert res2.status_code == 201


def test_allows_same_time_on_different_weekdays(client):
    """Verify identical time ranges on different weekdays do not conflict."""
    res_mon = client.post("/api/v1/availability", json={
        "day_of_week": "MONDAY",
        "start_time": "09:00:00",
        "end_time": "17:00:00",
    })
    assert res_mon.status_code == 201

    res_tue = client.post("/api/v1/availability", json={
        "day_of_week": "TUESDAY",
        "start_time": "09:00:00",
        "end_time": "17:00:00",
    })
    assert res_tue.status_code == 201


def test_list_and_filter_availability(client):
    """Verify listing all availability windows and filtering by day_of_week."""
    client.post("/api/v1/availability", json={"day_of_week": "FRIDAY", "start_time": "10:00:00", "end_time": "12:00:00"})
    client.post("/api/v1/availability", json={"day_of_week": "MONDAY", "start_time": "14:00:00", "end_time": "18:00:00"})
    client.post("/api/v1/availability", json={"day_of_week": "MONDAY", "start_time": "09:00:00", "end_time": "12:00:00"})

    # List all: should be ordered by weekday (Monday before Friday) and start_time
    res = client.get("/api/v1/availability")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 3
    assert items[0]["day_of_week"] == "MONDAY"
    assert items[0]["start_time"] == "09:00:00"
    assert items[1]["day_of_week"] == "MONDAY"
    assert items[1]["start_time"] == "14:00:00"
    assert items[2]["day_of_week"] == "FRIDAY"

    # Filter by Monday
    res_filter = client.get("/api/v1/availability?day_of_week=MONDAY")
    assert res_filter.status_code == 200
    mon_items = res_filter.json()
    assert len(mon_items) == 2
    assert all(item["day_of_week"] == "MONDAY" for item in mon_items)


def test_get_single_availability(client):
    """Verify retrieving a single availability window by ID."""
    created = client.post("/api/v1/availability", json={
        "day_of_week": "WEDNESDAY",
        "start_time": "09:00:00",
        "end_time": "11:00:00",
    }).json()

    res = client.get(f"/api/v1/availability/{created['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == created["id"]
    assert res.json()["day_of_week"] == "WEDNESDAY"

    # Nonexistent
    res_404 = client.get("/api/v1/availability/99999")
    assert res_404.status_code == 404


def test_update_availability(client):
    """Verify updating an availability window with validation and conflict checks."""
    created = client.post("/api/v1/availability", json={
        "day_of_week": "THURSDAY",
        "start_time": "09:00:00",
        "end_time": "12:00:00",
    }).json()

    # Valid update: extend window
    res_update = client.patch(f"/api/v1/availability/{created['id']}", json={
        "end_time": "13:00:00",
    })
    assert res_update.status_code == 200
    assert res_update.json()["end_time"] == "13:00:00"

    # Create another window on Thursday: 14:00 - 17:00
    res_second = client.post("/api/v1/availability", json={
        "day_of_week": "THURSDAY",
        "start_time": "14:00:00",
        "end_time": "17:00:00",
    })
    assert res_second.status_code == 201

    # Updating first window to overlap second (09:00 - 15:00) must return 409
    res_conflict = client.patch(f"/api/v1/availability/{created['id']}", json={
        "end_time": "15:00:00",
    })
    assert res_conflict.status_code == 409

    # Updating with start >= end must return error
    res_invalid = client.patch(f"/api/v1/availability/{created['id']}", json={
        "start_time": "14:00:00",
        "end_time": "10:00:00",
    })
    assert res_invalid.status_code in [400, 422]


def test_delete_availability(client):
    """Verify deleting an availability window."""
    created = client.post("/api/v1/availability", json={
        "day_of_week": "FRIDAY",
        "start_time": "13:00:00",
        "end_time": "16:00:00",
    }).json()

    # Delete
    del_res = client.delete(f"/api/v1/availability/{created['id']}")
    assert del_res.status_code == 204

    # Verify not found
    get_res = client.get(f"/api/v1/availability/{created['id']}")
    assert get_res.status_code == 404

    # Delete non-existent returns 404
    del_res2 = client.delete(f"/api/v1/availability/{created['id']}")
    assert del_res2.status_code == 404


def test_user_ownership_scoping(client):
    """Verify availability records are strictly scoped to the user."""
    # User 1 creates a window
    res1 = client.post(
        "/api/v1/availability",
        json={"day_of_week": "MONDAY", "start_time": "09:00:00", "end_time": "12:00:00"},
        headers={"X-User-Id": "1"},
    )
    assert res1.status_code == 201
    avail_id = res1.json()["id"]

    # User 2 creates identical time window on Monday: should SUCCEED because it's a different user!
    res2 = client.post(
        "/api/v1/availability",
        json={"day_of_week": "MONDAY", "start_time": "09:00:00", "end_time": "12:00:00"},
        headers={"X-User-Id": "2"},
    )
    assert res2.status_code == 201

    # User 2 cannot see User 1's window
    user2_get = client.get(f"/api/v1/availability/{avail_id}", headers={"X-User-Id": "2"})
    assert user2_get.status_code == 404

    # User 2 cannot update User 1's window
    user2_patch = client.patch(
        f"/api/v1/availability/{avail_id}",
        json={"end_time": "11:00:00"},
        headers={"X-User-Id": "2"},
    )
    assert user2_patch.status_code == 404

    # User 2 cannot delete User 1's window
    user2_delete = client.delete(f"/api/v1/availability/{avail_id}", headers={"X-User-Id": "2"})
    assert user2_delete.status_code == 404
