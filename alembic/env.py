"""
alembic/env.py — Alembic migration environment.

Alembic uses this file to know:
  1. WHERE is the database?  (sqlalchemy.url → our settings)
  2. WHAT tables exist?      (target_metadata → our Base)

We import `settings` and `Base` from our app so Alembic stays in sync
with the application code automatically.

Common commands:
  Generate a new migration after changing a model:
      uv run alembic revision --autogenerate -m "add description column"

  Apply all pending migrations:
      uv run alembic upgrade head

  Roll back the last migration:
      uv run alembic downgrade -1

  See current migration revision:
      uv run alembic current
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

# Import app models so Alembic can detect schema changes.
# This MUST come before target_metadata is set.
import app.models.task  # noqa: F401  — registers Task with Base.metadata
from alembic import context
from app.core.config import settings
from app.core.database import Base

# --------------------------------------------------------------------------- #
# Alembic Config object — provides access to alembic.ini values
# --------------------------------------------------------------------------- #
config = context.config

# Inject our DATABASE_URL from settings into Alembic config.
# This overrides the empty `sqlalchemy.url =` line in alembic.ini.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Set up Python logging from the alembic.ini logging section
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# `target_metadata` tells Alembic which tables to track for autogenerate.
target_metadata = Base.metadata


# --------------------------------------------------------------------------- #
# Migration runners
# --------------------------------------------------------------------------- #


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    In offline mode SQL is written to a file instead of executed.
    Useful when you want to review the SQL before running it on production.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In online mode Alembic connects to the real database and applies changes
    directly.  This is the default mode used in development and CI/CD.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
