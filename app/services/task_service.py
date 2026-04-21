"""
services/task_service.py — Business logic for task operations.

RESPONSIBILITY: Orchestrate repository calls + enforce business rules.
  • Calls TaskRepository for all DB access.
  • Raises HTTPException for "not found" and other business errors.
  • No SQL here.  No direct HTTP request/response parsing here.

Why a Service layer?
  • Business rules live in one testable place.
  • Routes stay thin — they just call the service and return the result.
  • When rules change (e.g. "can't delete completed tasks") you edit ONE file.

Example rule enforced here:
  get_task_or_404 → raises 404 automatically if a task doesn't exist.
  All operations that need a task reuse this helper.

Dependency flow:
  HTTP Request
    → endpoint (api/v1/endpoints/tasks.py)
    → TaskService  ← this file
    → TaskRepository (repositories/task_repository.py)
    → SQLAlchemy Session (core/database.py)
    → SQLite / PostgreSQL
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """Contains all business logic related to tasks."""

    def __init__(self, db: Session) -> None:
        # Instantiate the repository with the same DB session
        self.repo = TaskRepository(db)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _get_task_or_404(self, task_id: int) -> Task:
        """
        Fetch a task by ID, raising HTTP 404 if it does not exist.

        All public methods that need a task call this instead of
        calling the repo directly — keeps 404 logic in one place.
        """
        task = self.repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id={task_id} was not found.",
            )
        return task

    # ------------------------------------------------------------------ #
    # Public API (called by route handlers)
    # ------------------------------------------------------------------ #

    def list_tasks(self, skip: int = 0, limit: int = 100) -> list[Task]:
        """Return a paginated list of all tasks."""
        return self.repo.get_all(skip=skip, limit=limit)

    def get_task(self, task_id: int) -> Task:
        """Return one task or raise 404."""
        return self._get_task_or_404(task_id)

    def create_task(self, data: TaskCreate) -> Task:
        """Validate and persist a new task."""
        # Business rule example: strip extra whitespace from the title
        data.title = data.title.strip()
        return self.repo.create(data)

    def update_task(self, task_id: int, data: TaskUpdate) -> Task:
        """
        Update an existing task.

        `exclude_unset=True` means only fields the client explicitly
        sent are updated — the rest keep their current DB values.
        """
        task = self._get_task_or_404(task_id)
        update_fields = data.model_dump(exclude_unset=True)

        # Business rule: also strip whitespace if title is being updated
        if "title" in update_fields and update_fields["title"]:
            update_fields["title"] = update_fields["title"].strip()

        return self.repo.update(task, update_fields)

    def toggle_task(self, task_id: int) -> Task:
        """Flip the completed flag (True → False, False → True)."""
        task = self._get_task_or_404(task_id)
        return self.repo.toggle_completed(task)

    def delete_task(self, task_id: int) -> None:
        """Delete a task, raising 404 if it doesn't exist."""
        task = self._get_task_or_404(task_id)
        self.repo.delete(task)
