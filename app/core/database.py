"""
core/database.py — SQLAlchemy engine, session factory, and Base model.

Beginner Guide:
  Engine      → the raw connection to the database file/server.
  SessionLocal → a factory: call SessionLocal() to open a "unit of work".
  Base        → parent class that every ORM model inherits from.
                SQLAlchemy uses it to track all tables.

SQLite vs PostgreSQL:
  SQLite  needs `check_same_thread=False` because FastAPI is multi-threaded.
  Postgres doesn't need that arg — we detect which DB is in use automatically.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# --------------------------------------------------------------------------- #
# Engine
# --------------------------------------------------------------------------- #

# Build keyword args for the engine.
# SQLite needs check_same_thread=False; PostgreSQL does not need it.
_connect_args: dict = (
    {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    # `echo=True` logs every SQL query — useful for debugging, noisy in prod.
    echo=settings.DEBUG,
)

# --------------------------------------------------------------------------- #
# Session factory
# --------------------------------------------------------------------------- #

SessionLocal = sessionmaker(
    autocommit=False,   # never auto-commit — we control when to save
    autoflush=False,    # don't auto-flush before queries
    bind=engine,
)


# --------------------------------------------------------------------------- #
# Declarative Base
# --------------------------------------------------------------------------- #


class Base(DeclarativeBase):
    """
    All ORM models inherit from this class.

    When you run Base.metadata.create_all(engine), SQLAlchemy creates
    every table that has been defined as a subclass of Base.
    """

    pass
