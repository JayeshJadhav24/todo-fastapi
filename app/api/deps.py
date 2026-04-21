"""
api/deps.py — FastAPI dependency providers (dependency injection).

FastAPI's `Depends()` system calls these functions automatically and
injects the result into route handlers.

Why dependency injection?
  • Routes don't need to know HOW to create a session or service.
  • Swapping test dependencies is trivial (override in conftest.py).
  • Every request gets its own fresh session, closed when done.

Usage in any route:
    from fastapi import Depends
    from app.api.deps import get_task_service
    from app.services.task_service import TaskService

    def my_endpoint(service: TaskService = Depends(get_task_service)):
        return service.list_tasks()
"""

from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.task_service import TaskService

# --------------------------------------------------------------------------- #
# Database session dependency
# --------------------------------------------------------------------------- #


def get_db() -> Generator[Session, None, None]:
    """
    Open a DB session for one request, then close it automatically.

    The `yield` makes this a generator-based dependency:
      - Code before `yield` runs at the start of the request.
      - Code after  `yield` (in `finally`) runs after the response is sent.
    This guarantees no connection leaks even if an exception occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------------------------------------------------------------- #
# Service dependency (built on top of the DB session)
# --------------------------------------------------------------------------- #


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """
    Create and return a TaskService for one request.

    FastAPI resolves `get_db` first, then passes the session here.
    Routes only need to declare `Depends(get_task_service)` — they don't
    care how the session or service are created.
    """
    return TaskService(db)
