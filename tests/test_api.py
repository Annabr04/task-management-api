import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app import models

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Create clean tables before each test and drop after."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_task():
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


def test_list_tasks():
    client.post("/tasks", json={"title": "Task 1", "priority": "low"})
    client.post("/tasks", json={"title": "Task 2", "priority": "high"})
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_task():
    create = client.post("/tasks", json={"title": "Get me"})
    task_id = create.json()["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Get me"


def test_get_task_not_found():
    response = client.get("/tasks/9999")
    assert response.status_code == 404


def test_update_task():
    create = client.post("/tasks", json={"title": "Old title"})
    task_id = create.json()["id"]
    response = client.patch(
        f"/tasks/{task_id}", json={"title": "New title", "completed": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["completed"] is True


def test_delete_task():
    create = client.post("/tasks", json={"title": "Delete me"})
    task_id = create.json()["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    # Confirm it's gone
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_filter_by_completed():
    client.post("/tasks", json={"title": "Open task"})
    create = client.post("/tasks", json={"title": "Done task"})
    task_id = create.json()["id"]
    client.patch(f"/tasks/{task_id}", json={"completed": True})

    open_tasks = client.get("/tasks?completed=false")
    done_tasks = client.get("/tasks?completed=true")
    assert len(open_tasks.json()) == 1
    assert len(done_tasks.json()) == 1
