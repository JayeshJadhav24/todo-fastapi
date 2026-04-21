"""
models/task.py — SQLAlchemy ORM model for the Task table.

RESPONSIBILITY: Describes the database table ONLY.
  • No business logic here.
  • No validation here (that's Pydantic's job in schemas/).
  • No query logic here (that's the Repository's job).

The `Task` class maps 1-to-1 with the `tasks` table in SQLite/PostgreSQL.
Each attribute = one column.
"""

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Task(Base):
    """
    Represents a single to-do task in the database.

    Columns
    -------
    id          : Auto-incrementing integer primary key.
    title       : Required short title (max 255 chars).
    description : Optional extended notes (max 1 000 chars).
    completed   : True = done, False = pending.  Default: False.
    created_at  : UTC timestamp — set once on INSERT.
    updated_at  : UTC timestamp — refreshed on every UPDATE.
    """

    __tablename__ = "tasks"

    # Primary key — SQLAlchemy auto-increments this
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Required task title
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Optional description — Mapped[str | None] means it can be NULL in DB
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Completion flag
    completed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # `lambda` is used so each row gets the CURRENT time at insert time,
    # not the time Python imported this module.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __repr__(self) -> str:  # helpful for debugging in Python shell
        return f"<Task id={self.id!r} title={self.title!r} done={self.completed}>"
