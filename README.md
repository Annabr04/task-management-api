# Task Management API

## Live Demo

**Currently unavailable.** A hosted demo previously ran at <https://task-management-api-b7vo.onrender.com/>. As of 22 November 2026 that Render service is suspended, so the hosted API and `/docs` page are not available.

Use the one-command local demo below and open the interactive docs at <http://127.0.0.1:8000/docs>.

A clean, production-style REST API for managing tasks. Built with **FastAPI**, **SQLAlchemy**, and **SQLite**.

This project demonstrates core backend skills expected of a junior Python developer:
- RESTful API design
- Request/response validation with Pydantic
- Database models and sessions with SQLAlchemy
- Filtering & pagination
- Proper HTTP status codes and error handling
- Automated tests with pytest

**Requires Python 3.12 or later.** Continuous integration runs on Python 3.12.

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

Titles are stripped of surrounding whitespace and cannot be blank. `created_at` and `updated_at` are UTC and serialized as ISO 8601 with a `Z` suffix. List results are ordered by `created_at` descending, then `id` descending so pagination stays stable when timestamps match.

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

### One-command local demo

From the project root, with the virtual environment activated and dependencies installed:

```bash
python scripts/seed.py && uvicorn app.main:app
```

This loads five synthetic (fictional) tasks and starts the API at <http://127.0.0.1:8000>. If `tasks.db` already has rows, the seed script leaves them unchanged; pass `--reset` to replace them with the demo set. Then try `/docs` or the curl examples below.

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

The suite uses a temporary SQLite database. It does not read or write `./tasks.db`.

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
├── scripts/
│   └── seed.py          # Synthetic local-demo data
├── tests/
│   ├── conftest.py      # Temp-DB fixtures
│   └── test_api.py      # pytest suite
├── .github/
│   └── workflows/
│       └── tests.yml    # CI
├── .gitignore
├── LICENSE
├── pytest.ini
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

## License

MIT. See [LICENSE](LICENSE).
