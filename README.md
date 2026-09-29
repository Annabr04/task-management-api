# Task Management API

## Live Demo

🚀 **Live API**: [[https://your-url.onrender.com](https://task-management-api-b7vo.onrender.com/)]

📖 **Interactive Docs**: [https://task-management-api-b7vo.onrender.com/docs]([https://your-url.onrender.com/docs])


A clean, production-style REST API for managing tasks. Built with **FastAPI**, **SQLAlchemy**, and **SQLite**.

This project demonstrates core backend skills expected of a junior Python developer:
- RESTful API design
- Request/response validation with Pydantic
- Database models and sessions with SQLAlchemy
- Filtering & pagination
- Proper HTTP status codes and error handling
- Automated tests with pytest

---

## Features

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/tasks` | POST | Create a task |
| `/tasks` | GET | List tasks (supports filters + pagination) |
| `/tasks/{id}` | GET | Get a single task |
| `/tasks/{id}` | PATCH | Partially update a task |
| `/tasks/{id}` | DELETE | Delete a task |

**Task fields:** `title`, `description`, `priority` (`low` / `medium` / `high`), `completed`, timestamps.

---

## Quick Start

```bash
# 1. Clone / enter the project
cd task-management-api

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
uvicorn app.main:app --reload
```

Open interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Example Usage

**Create a task**
```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Ship the resume", "priority": "high"}'
```

**List open high-priority tasks**
```bash
curl "http://127.0.0.1:8000/tasks?completed=false&priority=high"
```

**Mark a task complete**
```bash
curl -X PATCH http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

---

## Running Tests

```bash
pytest -v
```

---

## Project Structure

```
task-management-api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI routes
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   └── database.py      # DB engine & session
├── tests/
│   └── test_api.py      # pytest suite
├── requirements.txt
└── README.md
```

---

## What I Learned / Focus Areas

- Designing clear REST endpoints and status codes
- Using Pydantic for robust input validation
- SQLAlchemy 2.0 style models and dependency injection
- Writing meaningful automated tests
- Keeping the codebase small, readable, and easy to extend

---

## Future Improvements

- Add user authentication (JWT)
- Switch to PostgreSQL
- Add Docker support
- Rate limiting and better logging

---

Built as a portfolio project for junior Python / backend developer roles.
