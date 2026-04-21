# Todo FastAPI — Professional Backend

A production-style **To-Do REST API** built with **FastAPI**, following clean
architecture principles: Repository → Service → Router.

Built for learning, structured for production.

---

## Architecture Overview

```
HTTP Request
  ↓
api/v1/endpoints/tasks.py   ← handles HTTP only (thin routes)
  ↓
services/task_service.py    ← business logic (404 checks, rules)
  ↓
repositories/task_repository.py  ← raw database queries only
  ↓
SQLAlchemy Session (core/database.py)
  ↓
SQLite / PostgreSQL
```

### Why Repository + Service Pattern?

| Without It | With It |
|---|---|
| SQL in routes | SQL only in Repository |
| Business logic scattered | Business logic only in Service |
| Hard to test | Easy to mock/test each layer |
| Hard to swap DB | Swap DB by changing Repository only |
| Spaghetti code fast | Clean, grows gracefully |

---

## Project Structure

```
todo-fastapi/
├── app/
│   ├── main.py                        # App entry point
│   ├── api/
│   │   ├── deps.py                    # Dependency injection (get_db, get_service)
│   │   └── v1/
│   │       ├── api.py                 # Router aggregator
│   │       └── endpoints/
│   │           └── tasks.py          # HTTP endpoints (thin)
│   ├── core/
│   │   ├── config.py                  # pydantic-settings (reads .env)
│   │   ├── database.py                # SQLAlchemy engine + session
│   │   └── security.py                # Placeholder for future auth
│   ├── models/
│   │   └── task.py                    # SQLAlchemy ORM model (DB table)
│   ├── schemas/
│   │   └── task.py                    # Pydantic request/response models
│   ├── repositories/
│   │   └── task_repository.py         # Raw DB queries only
│   ├── services/
│   │   └── task_service.py            # Business logic only
│   ├── utils/
│   │   └── helpers.py                 # Generic utilities
│   └── tests/
│       ├── conftest.py                # Shared fixtures
│       ├── test_unit.py               # Unit tests (repository + service)
│       ├── test_integration.py        # API endpoint tests
│       └── test_e2e.py                # Full user flow tests
├── alembic/                           # Database migrations
├── .github/workflows/ci.yml           # GitHub Actions CI/CD
├── .env                               # Local secrets (NOT committed)
├── .env.example                       # Template (committed)
├── pyproject.toml                     # Project + tool config
└── .gitignore
```

---

## Quick Start

### 1. Install UV

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and set up the project

```bash
git clone https://github.com/YOUR_USERNAME/todo-fastapi.git
cd todo-fastapi
```

### 3. Create virtual environment and install dependencies

```bash
# Create .venv in the project directory
uv venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# Install all dependencies (runtime + dev)
uv sync --all-extras
```

### 4. Configure environment

```bash
# Copy the example file
cp .env.example .env
# Edit .env if needed (defaults work for SQLite development)
```

### 5. Run the server

```bash
uv run uvicorn app.main:app --reload
```

Open your browser:
- **Swagger UI** → http://127.0.0.1:8000/docs
- **ReDoc**       → http://127.0.0.1:8000/redoc
- **Health**      → http://127.0.0.1:8000/health

---

## UV Commands Reference

```bash
# Add a new runtime package
uv add requests

# Add a dev-only package
uv add --dev black

# Remove a package
uv remove requests

# Update all packages
uv lock --upgrade

# Run any command inside the venv (without activating)
uv run python -m app.main
uv run pytest
uv run ruff check .
```

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/tasks/` | List all tasks |
| `POST` | `/api/v1/tasks/` | Create a task |
| `GET` | `/api/v1/tasks/{id}` | Get task by ID |
| `PUT` | `/api/v1/tasks/{id}` | Update a task |
| `PATCH` | `/api/v1/tasks/{id}/toggle` | Toggle completed |
| `DELETE` | `/api/v1/tasks/{id}` | Delete a task |

---

## Running Tests

```bash
# Run ALL tests with coverage
uv run pytest

# Run specific test levels
uv run pytest app/tests/test_unit.py -v
uv run pytest app/tests/test_integration.py -v
uv run pytest app/tests/test_e2e.py -v

# Coverage report only
uv run pytest --cov=app --cov-report=html
# Then open: htmlcov/index.html
```

---

## Linting

```bash
# Check for lint errors
uv run ruff check .

# Auto-fix safe issues
uv run ruff check . --fix

# Check formatting
uv run ruff format --check .

# Auto-format
uv run ruff format .
```

---

## Database Migrations (Alembic)

```bash
# Apply all pending migrations (first time: creates tables)
uv run alembic upgrade head

# Generate a migration after you change a model
uv run alembic revision --autogenerate -m "add priority column to tasks"

# Roll back the last migration
uv run alembic downgrade -1

# See current revision
uv run alembic current

# See migration history
uv run alembic history
```

> **Development shortcut**: The app auto-creates tables on startup via
> `Base.metadata.create_all()`. For real migrations (schema changes),
> always use Alembic.

---

## Git Branching Strategy

### Branch Types

| Branch | Purpose | Who creates it |
|--------|---------|----------------|
| `main` | Production-ready code only | Merge from `develop` via PR |
| `develop` | Integration branch — latest working code | Merge features here first |
| `feature/xxx` | New feature development | Developer |
| `hotfix/xxx` | Urgent production bug fix | Developer |

### When to Use Each Branch

- **`main`**: Only stable, fully tested code. Never commit directly here.
- **`develop`**: Features are merged here. Acts as "staging".
- **`feature/add-auth`**: Developing a new authentication system.
- **`feature/improve-tests`**: Adding/improving test coverage.
- **`hotfix/bug-001`**: Critical bug in production that can't wait for the next release.

### Setup Commands

```bash
# 1. Initialise a new repo
git init
git add .
git commit -m "chore: initial project setup"

# 2. Create and switch to develop
git checkout -b develop

# 3. Create a feature branch from develop
git checkout develop
git checkout -b feature/add-auth

# 4. Work on the feature, then merge back to develop
git checkout develop
git merge feature/add-auth
git branch -d feature/add-auth   # clean up local branch

# 5. When develop is stable, merge to main
git checkout main
git merge develop

# 6. Connect to GitHub
git remote add origin https://github.com/YOUR_USERNAME/todo-fastapi.git
git push -u origin main
git push origin develop

# 7. Create remaining branches on remote
git checkout -b feature/improve-tests
git push origin feature/improve-tests

git checkout -b hotfix/bug-001
git push origin hotfix/bug-001
```

---

## CI/CD Pipeline Explained

Every `git push` to `main` or `develop` (and every Pull Request) triggers
the GitHub Actions pipeline defined in `.github/workflows/ci.yml`.

```
Push / PR
  │
  ▼
┌─────────────────────────────────────────┐
│  Job: test  (runs on Python 3.11 + 3.12 │
│  in parallel)                            │
│                                          │
│  1. Checkout code                        │
│  2. Install uv                           │
│  3. Install dependencies                 │
│  4. Ruff lint      ← QUALITY GATE       │
│  5. Ruff format check                    │
│  6. Unit tests                           │
│  7. Integration tests                    │
│  8. E2E tests                            │
│  9. Coverage report                      │
└─────────────────────────────────────────┘
  │
  ▼
✅ All green → safe to merge
❌ Any fail  → PR cannot be merged
```

**Key concept**: The lint step is a **quality gate**. If code doesn't pass
Ruff, the whole pipeline fails and no one can merge broken code.

---

## Switching to PostgreSQL

The codebase is already structured to support PostgreSQL. To switch:

1. Install the driver:
   ```bash
   uv add psycopg2-binary
   ```

2. Update `.env`:
   ```
   DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/todo_db
   ```

3. Remove the SQLite-only logic:
   - In `core/database.py`, the `check_same_thread` arg is auto-excluded for non-SQLite URLs (already handled).

4. Run migrations:
   ```bash
   uv run alembic upgrade head
   ```

That's it — no other code changes needed.

---

## Extending the Project

### Add a new resource (e.g., Categories)

1. `app/models/category.py` — SQLAlchemy model
2. `app/schemas/category.py` — Pydantic schemas
3. `app/repositories/category_repository.py` — DB queries
4. `app/services/category_service.py` — Business logic
5. `app/api/v1/endpoints/categories.py` — HTTP endpoints
6. Register in `app/api/v1/api.py`
7. Generate migration: `uv run alembic revision --autogenerate -m "add categories"`

### Add Authentication

1. Uncomment `core/security.py`
2. Add `uv add passlib[bcrypt] python-jose[cryptography]`
3. Create `app/models/user.py`
4. Add auth endpoints in `app/api/v1/endpoints/auth.py`
5. Add `Depends(get_current_user)` to protected routes

---

## Requirements at a Glance

```
Runtime:  fastapi  uvicorn  sqlalchemy  alembic  pydantic-settings
Dev:      pytest   pytest-cov  httpx  ruff
```

All managed with **UV** — no `pip`, no `requirements.txt` needed.
