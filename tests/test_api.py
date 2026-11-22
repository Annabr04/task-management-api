from datetime import datetime, timezone
from pathlib import Path

from app import models


def assert_utc_iso(value: str) -> datetime:
    assert isinstance(value, str)
    assert value.endswith("Z") or value.endswith("+00:00")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None
    assert parsed.utcoffset() is not None
    assert parsed.utcoffset().total_seconds() == 0
    return parsed


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_task(client):
    payload = {
        "title": "Write tests",
        "description": "Add unit tests for the API",
        "priority": "high",
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Write tests"
    assert data["priority"] == "high"
    assert data["completed"] is False
    assert "id" in data
    assert_utc_iso(data["created_at"])
    assert_utc_iso(data["updated_at"])


def test_list_tasks(client):
    client.post("/tasks", json={"title": "Task 1", "priority": "low"})
    client.post("/tasks", json={"title": "Task 2", "priority": "high"})
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_get_task(client):
    create = client.post("/tasks", json={"title": "Get me"})
    task_id = create.json()["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Get me"


def test_get_task_not_found(client):
    response = client.get("/tasks/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_task(client):
    create = client.post("/tasks", json={"title": "Old title"})
    task_id = create.json()["id"]
    response = client.patch(
        f"/tasks/{task_id}", json={"title": "New title", "completed": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["completed"] is True


def test_update_task_not_found(client):
    response = client.patch("/tasks/9999", json={"title": "nope"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_delete_task(client):
    create = client.post("/tasks", json={"title": "Delete me"})
    task_id = create.json()["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_delete_task_not_found(client):
    response = client.delete("/tasks/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_filter_by_completed(client):
    client.post("/tasks", json={"title": "Open task"})
    create = client.post("/tasks", json={"title": "Done task"})
    task_id = create.json()["id"]
    client.patch(f"/tasks/{task_id}", json={"completed": True})

    open_tasks = client.get("/tasks?completed=false")
    done_tasks = client.get("/tasks?completed=true")
    assert len(open_tasks.json()) == 1
    assert len(done_tasks.json()) == 1


def test_filter_by_priority(client):
    client.post("/tasks", json={"title": "Low", "priority": "low"})
    client.post("/tasks", json={"title": "Medium", "priority": "medium"})
    client.post("/tasks", json={"title": "High", "priority": "high"})

    high = client.get("/tasks?priority=high")
    assert high.status_code == 200
    assert len(high.json()) == 1
    assert high.json()[0]["title"] == "High"

    low = client.get("/tasks?priority=low")
    assert len(low.json()) == 1
    assert low.json()[0]["priority"] == "low"

    invalid = client.get("/tasks?priority=urgent")
    assert invalid.status_code == 400


def test_filter_by_priority_and_completed(client):
    client.post("/tasks", json={"title": "Open high", "priority": "high"})
    done = client.post("/tasks", json={"title": "Done high", "priority": "high"})
    client.patch(f"/tasks/{done.json()['id']}", json={"completed": True})
    client.post("/tasks", json={"title": "Open low", "priority": "low"})

    high_done = client.get("/tasks?priority=high&completed=true")
    high_open = client.get("/tasks?priority=high&completed=false")
    assert [t["title"] for t in high_done.json()] == ["Done high"]
    assert [t["title"] for t in high_open.json()] == ["Open high"]


def test_pagination_skip_and_limit(client):
    for i in range(5):
        client.post("/tasks", json={"title": f"Task {i}"})
    # Default order is created_at desc, id desc, so newest first.
    page = client.get("/tasks?skip=1&limit=2")
    assert page.status_code == 200
    data = page.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task 3"
    assert data[1]["title"] == "Task 2"
    zero = client.get("/tasks?limit=0")
    # limit ge=1, so invalid should 422
    assert zero.status_code == 422


def test_pagination_past_the_end(client):
    client.post("/tasks", json={"title": "Only one"})
    response = client.get("/tasks?skip=50&limit=10")
    assert response.status_code == 200
    assert response.json() == []


def test_pagination_bounds_rejected(client):
    assert client.get("/tasks?skip=-1").status_code == 422
    assert client.get("/tasks?limit=0").status_code == 422
    assert client.get("/tasks?limit=101").status_code == 422


def test_pagination_tie_break_on_equal_timestamps(client, db_session):
    fixed = datetime(2026, 11, 22, 15, 0, 0, tzinfo=timezone.utc)
    for i in range(5):
        db_session.add(
            models.Task(title=f"Same {i}", created_at=fixed, updated_at=fixed)
        )
    db_session.commit()

    page = client.get("/tasks?skip=1&limit=2")
    assert page.status_code == 200
    assert [t["title"] for t in page.json()] == ["Same 3", "Same 2"]

    full = client.get("/tasks")
    assert [t["title"] for t in full.json()] == [f"Same {i}" for i in range(4, -1, -1)]
    ids = [t["id"] for t in full.json()]
    assert ids == sorted(ids, reverse=True)


def test_create_validation_errors(client):
    missing = client.post("/tasks", json={"priority": "high"})
    assert missing.status_code == 422

    empty = client.post("/tasks", json={"title": ""})
    assert empty.status_code == 422

    too_long_title = client.post("/tasks", json={"title": "A" * 201})
    assert too_long_title.status_code == 422

    ok_len = client.post("/tasks", json={"title": "A" * 200})
    assert ok_len.status_code == 201

    too_long_desc = client.post(
        "/tasks", json={"title": "ok", "description": "D" * 1001}
    )
    assert too_long_desc.status_code == 422

    invalid_priority = client.post(
        "/tasks", json={"title": "ok", "priority": "urgent"}
    )
    assert invalid_priority.status_code == 422


def test_create_rejects_whitespace_only_title(client):
    for title in ("   ", "\t", "\n", " \t\n "):
        response = client.post("/tasks", json={"title": title})
        assert response.status_code == 422, title


def test_create_strips_title_whitespace(client):
    response = client.post("/tasks", json={"title": "  Trim me  "})
    assert response.status_code == 201
    assert response.json()["title"] == "Trim me"


def test_patch_rejects_whitespace_only_title(client):
    created = client.post("/tasks", json={"title": "ok"})
    task_id = created.json()["id"]
    response = client.patch(f"/tasks/{task_id}", json={"title": "   "})
    assert response.status_code == 422
    assert client.get(f"/tasks/{task_id}").json()["title"] == "ok"


def test_patch_strips_title_whitespace(client):
    created = client.post("/tasks", json={"title": "ok"})
    task_id = created.json()["id"]
    response = client.patch(f"/tasks/{task_id}", json={"title": "  Updated  "})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


def test_invalid_path_id(client):
    assert client.get("/tasks/abc").status_code == 422


def test_timestamps_are_utc_with_explicit_offset(client):
    created = client.post("/tasks", json={"title": "timed"}).json()
    assert_utc_iso(created["created_at"])
    assert_utc_iso(created["updated_at"])

    fetched = client.get(f"/tasks/{created['id']}").json()
    assert_utc_iso(fetched["created_at"])
    assert_utc_iso(fetched["updated_at"])
    listed = client.get("/tasks").json()[0]
    assert_utc_iso(listed["created_at"])
    assert_utc_iso(listed["updated_at"])


def test_updated_at_changes_on_patch(client):
    created = client.post("/tasks", json={"title": "orig"}).json()
    updated = client.patch(
        f"/tasks/{created['id']}", json={"title": "new"}
    ).json()
    assert updated["created_at"] == created["created_at"]
    assert updated["updated_at"] != created["updated_at"]
    assert_utc_iso(updated["updated_at"])
    assert assert_utc_iso(updated["updated_at"]) >= assert_utc_iso(created["updated_at"])


def test_does_not_touch_default_tasks_db(client):
    """The suite must not create, drop, or write the developer's ./tasks.db."""
    cwd_sentinel = Path.cwd() / "tasks.db"
    repo_sentinel = Path(__file__).resolve().parents[1] / "tasks.db"
    paths = []
    for path in dict.fromkeys((cwd_sentinel, repo_sentinel)):
        if path.exists():
            paths.append((path, path.read_bytes(), path.stat()))

    response = client.post("/tasks", json={"title": "isolation probe"})
    assert response.status_code == 201
    assert client.get("/tasks").status_code == 200
    assert client.delete(f"/tasks/{response.json()['id']}").status_code == 204

    for path, before, before_stat in paths:
        after_stat = path.stat()
        assert path.read_bytes() == before, f"{path} contents changed"
        assert after_stat.st_mtime_ns == before_stat.st_mtime_ns, f"{path} mtime changed"
        assert after_stat.st_size == before_stat.st_size, f"{path} size changed"
        assert after_stat.st_ino == before_stat.st_ino, f"{path} inode changed"

    # If the developer has no tasks.db, tests must not create one in cwd
    # (unless a fixture/user already placed a sentinel we just verified).
    if not paths:
        assert not cwd_sentinel.exists()
