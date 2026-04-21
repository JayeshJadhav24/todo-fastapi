"""
tests/conftest.py — Shared pytest fixtures.

Fixtures defined here are automatically available in ALL test files
in this directory without importing them manually.

What we provide:
  db       → an isolated in-memory SQLite session per test
  client   → a FastAPI TestClient that uses `db` instead of the real DB

Why override `get_db`?
  If we used the real `todo.db`, tests would pollute each other and
  leave data behind.  By overriding the dependency, every test gets a
  fresh empty database that is destroyed when the test ends.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_db
from app.core.database import Base
from app.main import app

# Use an in-memory SQLite database for isolation.
# ":memory:" means the DB lives in RAM — fast and auto-deleted after the test.
TEST_DATABASE_URL = "sqlite:///./test_todo.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="function")
def db() -> Session:
    """
    Provide a clean database session for one test function.

    `scope="function"` means a fresh session (and fresh tables) for EACH test.
    This prevents tests from affecting each other.
    """
    # Create all tables before the test
    Base.metadata.create_all(bind=test_engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after the test — start fresh next time
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db: Session) -> TestClient:
    """
    Provide a FastAPI TestClient wired to the test database.

    We override the `get_db` dependency so routes use the test session,
    not the real production session.

    `app.dependency_overrides` is FastAPI's official way to swap
    any Depends() for testing.
    """

    def _override_get_db():
        try:
            yield db
        finally:
            pass  # session is closed by the `db` fixture

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as c:
        yield c

    # Clean up — remove overrides after each test
    app.dependency_overrides.clear()
