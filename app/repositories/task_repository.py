"""
repositories/task_repository.py — Raw database queries for Task.

RESPONSIBILITY: One place for ALL database access.
  • Speak SQL (via SQLAlchemy ORM).
  • Return ORM objects or None/bool.
  • No business logic, no HTTP knowledge.

Why a Repository layer?
  • If you swap SQLite for PostgreSQL, you change only this file.
  • It is easy to mock in unit tests (pass a fake session).
  • Routes and services stay clean — zero SQL in them.

Pattern: pass `db: Session` in the constructor.
The session is created per HTTP request by the dependency in api/deps.py.
"""

from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate


class TaskRepository:
    """Encapsulates all database operations for the Task table."""

    def __init__(self, db: Session) -> None:
        # Store the session — every method uses it
        self.db = db

    # ------------------------------------------------------------------ #
    # READ
    # ------------------------------------------------------------------ #

    def get_by_id(self, task_id: int) -> Task | None:
        """
        Fetch a single task by primary key.
        Returns None if not found (caller decides what to do).
        """
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Task]:
        """
        Fetch a paginated list of tasks.

        Parameters
        ----------
        skip   : rows to skip (offset);  useful for page 2, 3 …
        limit  : max rows to return;     prevents returning millions of rows
        """
        return self.db.query(Task).offset(skip).limit(limit).all()

    # ------------------------------------------------------------------ #
    # CREATE
    # ------------------------------------------------------------------ #

    def create(self, task_data: TaskCreate) -> Task:
        """
        Insert a new task row.

        Flow:
          1. Build a Task ORM object from schema data.
          2. Add it to the session (marks it for INSERT).
          3. Commit — write to disk.
          4. Refresh — reload the row to get DB-generated id, created_at, etc.
        """
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
        )
        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        return new_task

    # ------------------------------------------------------------------ #
    # UPDATE
    # ------------------------------------------------------------------ #

    def update(self, task: Task, update_fields: dict) -> Task:
        """
        Apply a dict of field → value pairs to an existing task.

        `update_fields` comes from `schema.model_dump(exclude_unset=True)`,
        meaning it only contains values the client explicitly sent.
        """
        for field, value in update_fields.items():
            setattr(task, field, value)

        self.db.commit()
        self.db.refresh(task)
        return task

    def toggle_completed(self, task: Task) -> Task:
        """Flip completed: False → True or True → False."""
        task.completed = not task.completed
        self.db.commit()
        self.db.refresh(task)
        return task

    # ------------------------------------------------------------------ #
    # DELETE
    # ------------------------------------------------------------------ #

    def delete(self, task: Task) -> None:
        """Remove a task row from the database permanently."""
        self.db.delete(task)
        self.db.commit()
