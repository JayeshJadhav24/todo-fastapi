"""
tests/test_unit.py — Unit tests for Repository and Service layers.

WHAT is a unit test?
  A test that checks ONE small piece of logic in ISOLATION.
  We pass a real DB session so we can test real SQL, but we use an
  in-memory SQLite database (set up in conftest.py) so it's fast and
  isolated from the production database.

WHAT do we test here?
  • TaskRepository  — does it save, fetch, update, toggle, delete correctly?
  • TaskService     — does it apply business rules correctly?
                      does it raise 404 for missing tasks?

WHY no HTTP here?
  Unit tests are faster and pinpoint EXACTLY where a bug is.
  Integration tests handle HTTP behaviour (see test_integration.py).

Run with:
    uv run pytest app/tests/test_unit.py -v
"""

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService

# =========================================================================== #
# TaskRepository tests
# =========================================================================== #


class TestTaskRepository:
    """Test every method of TaskRepository using a real (test) DB session."""

    def test_create_task(self, db: Session) -> None:
        """A new task should be persisted and returned with an auto-generated id."""
        repo = TaskRepository(db)
        data = TaskCreate(title="Buy milk", description="Whole milk")

        task = repo.create(data)

        assert task.id is not None
        assert task.title == "Buy milk"
        assert task.description == "Whole milk"
        assert task.completed is False

    def test_get_by_id_returns_task(self, db: Session) -> None:
        """get_by_id should return the task when it exists."""
        repo = TaskRepository(db)
        created = repo.create(TaskCreate(title="Task A"))

        fetched = repo.get_by_id(created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.title == "Task A"

    def test_get_by_id_returns_none_for_missing(self, db: Session) -> None:
        """get_by_id should return None (not raise) when task doesn't exist."""
        repo = TaskRepository(db)

        result = repo.get_by_id(99999)

        assert result is None

    def test_get_all_returns_list(self, db: Session) -> None:
        """get_all should return all tasks in the database."""
        repo = TaskRepository(db)
        repo.create(TaskCreate(title="Task 1"))
        repo.create(TaskCreate(title="Task 2"))
        repo.create(TaskCreate(title="Task 3"))

        tasks = repo.get_all()

        assert len(tasks) == 3

    def test_get_all_pagination(self, db: Session) -> None:
        """skip and limit should correctly paginate results."""
        repo = TaskRepository(db)
        for i in range(5):
            repo.create(TaskCreate(title=f"Task {i}"))

        page = repo.get_all(skip=2, limit=2)

        assert len(page) == 2

    def test_update_task_fields(self, db: Session) -> None:
        """update should modify only the provided fields."""
        repo = TaskRepository(db)
        task = repo.create(TaskCreate(title="Original title"))

        updated = repo.update(task, {"title": "Updated title", "completed": True})

        assert updated.title == "Updated title"
        assert updated.completed is True

    def test_toggle_completed(self, db: Session) -> None:
        """toggle_completed should flip False → True → False."""
        repo = TaskRepository(db)
        task = repo.create(TaskCreate(title="Flip me"))
        assert task.completed is False

        toggled = repo.toggle_completed(task)
        assert toggled.completed is True

        toggled_back = repo.toggle_completed(toggled)
        assert toggled_back.completed is False

    def test_delete_task(self, db: Session) -> None:
        """After delete, get_by_id should return None."""
        repo = TaskRepository(db)
        task = repo.create(TaskCreate(title="Delete me"))
        task_id = task.id

        repo.delete(task)

        assert repo.get_by_id(task_id) is None


# =========================================================================== #
# TaskService tests
# =========================================================================== #


class TestTaskService:
    """Test TaskService business logic."""

    def test_create_task_strips_whitespace(self, db: Session) -> None:
        """Service should strip leading/trailing whitespace from title."""
        service = TaskService(db)
        data = TaskCreate(title="  Clean me up  ")

        task = service.create_task(data)

        assert task.title == "Clean me up"

    def test_get_task_raises_404_for_missing(self, db: Session) -> None:
        """get_task should raise HTTPException 404 when task doesn't exist."""
        service = TaskService(db)

        with pytest.raises(HTTPException) as exc_info:
            service.get_task(99999)

        assert exc_info.value.status_code == 404
        assert "99999" in exc_info.value.detail

    def test_update_task_only_changes_provided_fields(self, db: Session) -> None:
        """Updating only `completed` should not change the title."""
        service = TaskService(db)
        task = service.create_task(TaskCreate(title="Keep this title"))

        updated = service.update_task(task.id, TaskUpdate(completed=True))

        assert updated.title == "Keep this title"
        assert updated.completed is True

    def test_toggle_task(self, db: Session) -> None:
        """toggle_task should invert the completed flag."""
        service = TaskService(db)
        task = service.create_task(TaskCreate(title="Toggle me"))
        assert task.completed is False

        toggled = service.toggle_task(task.id)
        assert toggled.completed is True

    def test_toggle_missing_task_raises_404(self, db: Session) -> None:
        """toggle_task should raise 404 for non-existent task."""
        service = TaskService(db)

        with pytest.raises(HTTPException) as exc_info:
            service.toggle_task(99999)

        assert exc_info.value.status_code == 404

    def test_delete_task(self, db: Session) -> None:
        """After delete_task, get_task should raise 404."""
        service = TaskService(db)
        task = service.create_task(TaskCreate(title="Bye"))
        task_id = task.id

        service.delete_task(task_id)

        with pytest.raises(HTTPException) as exc_info:
            service.get_task(task_id)
        assert exc_info.value.status_code == 404

    def test_delete_missing_task_raises_404(self, db: Session) -> None:
        """Deleting a non-existent task should raise 404."""
        service = TaskService(db)

        with pytest.raises(HTTPException) as exc_info:
            service.delete_task(99999)

        assert exc_info.value.status_code == 404
