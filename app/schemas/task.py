"""
schemas/task.py — Pydantic request & response models for Task.

RESPONSIBILITY: Validate data coming IN and serialize data going OUT.
  • No DB columns here — that's models/task.py.
  • No business logic — that's services/task_service.py.

Why separate schemas from models?
  • You may want to expose only some columns (hide `created_at` on create).
  • You may want different validation rules for create vs update.
  • Pydantic and SQLAlchemy have different purposes — keep them separate.

Schema hierarchy:
  TaskBase          → shared fields
  ├── TaskCreate    → POST body   (inherits title + description)
  ├── TaskUpdate    → PUT  body   (all fields optional)
  └── TaskResponse  → all output  (adds id, completed, timestamps)
"""

from datetime import datetime

from pydantic import BaseModel, Field

# --------------------------------------------------------------------------- #
# Base — shared fields
# --------------------------------------------------------------------------- #


class TaskBase(BaseModel):
    """Fields used in both creating and reading tasks."""

    title: str = Field(
        ...,            # required (no default)
        min_length=1,
        max_length=255,
        description="Short task title",
        examples=["Buy groceries"],
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional longer description",
        examples=["Milk, eggs, bread from the store"],
    )


# --------------------------------------------------------------------------- #
# Request schemas (data coming IN from the client)
# --------------------------------------------------------------------------- #


class TaskCreate(TaskBase):
    """
    Body for POST /api/v1/tasks.

    Inherits `title` (required) and `description` (optional) from TaskBase.
    Nothing extra — keep it simple.
    """

    pass


class TaskUpdate(BaseModel):
    """
    Body for PUT /api/v1/tasks/{id}.

    ALL fields are optional — the client sends only what they want to change.
    `model_dump(exclude_unset=True)` in the service will filter out untouched fields.
    """

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool | None = None


# --------------------------------------------------------------------------- #
# Response schemas (data going OUT to the client)
# --------------------------------------------------------------------------- #


class TaskResponse(TaskBase):
    """
    Shape of every task returned by the API.

    `model_config = {"from_attributes": True}` enables ORM mode:
    Pydantic reads values from SQLAlchemy model attributes,
    not just plain dicts.  Required for all response models.
    """

    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    """Generic response for operations that don't return a Task (e.g., DELETE)."""

    message: str
