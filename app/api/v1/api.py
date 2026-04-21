"""
api/v1/api.py — Router aggregator for API version 1.

This file acts as a "hub" that collects all v1 endpoint routers
into a single `api_router`.  main.py then mounts this under /api/v1.

Adding a new resource (e.g. users) in the future:
  from app.api.v1.endpoints import users
  api_router.include_router(users.router, prefix="/users", tags=["Users"])
"""

from fastapi import APIRouter

from app.api.v1.endpoints import tasks

# All v1 routes are grouped under this router
api_router = APIRouter()

api_router.include_router(
    tasks.router,
    prefix="/tasks",   # every task endpoint starts with /api/v1/tasks
    tags=["Tasks"],    # groups endpoints in Swagger UI
)
