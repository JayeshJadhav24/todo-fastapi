"""
main.py — FastAPI application entry point.

RESPONSIBILITY: Wire everything together.
  1. Create the FastAPI app instance with metadata.
  2. Register the lifespan (startup / shutdown hooks).
  3. Mount the v1 API router under /api/v1.
  4. Add the top-level /health endpoint.

Run the development server:
    uvicorn app.main:app --reload

Interactive API docs:
    http://127.0.0.1:8000/docs   ← Swagger UI (try endpoints in browser)
    http://127.0.0.1:8000/redoc  ← ReDoc (read-friendly docs)

Architecture flow:
    Request → main.py → api/v1/api.py → endpoints/tasks.py
           → TaskService → TaskRepository → SQLAlchemy → SQLite
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import Base, engine

# --------------------------------------------------------------------------- #
# Lifespan — startup & shutdown hooks
# --------------------------------------------------------------------------- #


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Code BEFORE `yield`  → runs once when the server starts.
    Code AFTER  `yield`  → runs once when the server shuts down.

    Development: `create_all` auto-creates tables from ORM models.
    Production:  Remove `create_all` and use Alembic migrations instead.
                 (See README — "Database Migrations" section.)
    """
    # --- STARTUP ---
    Base.metadata.create_all(bind=engine)  # create tables if they don't exist
    yield
    # --- SHUTDOWN --- (nothing to clean up for SQLite)


# --------------------------------------------------------------------------- #
# App instance
# --------------------------------------------------------------------------- #

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "A production-style To-Do REST API built with FastAPI, SQLAlchemy, "
        "and clean architecture (Repository + Service pattern)."
    ),
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Mount all /api/v1/... routes
# prefix="/api/v1" is defined in settings so it's easy to change
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# --------------------------------------------------------------------------- #
# Health check  (top-level — outside /api/v1 prefix)
# --------------------------------------------------------------------------- #


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    response_model=dict,
)
def health_check() -> dict:
    """
    Lightweight endpoint to verify the API is up.

    Used by:
      • CI/CD pipelines after deployment.
      • Load balancers / monitoring tools.
      • Docker HEALTHCHECK instructions.
    """
    return {"status": "ok", "app": settings.APP_NAME}
