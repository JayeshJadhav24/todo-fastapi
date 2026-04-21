"""
api/v1/endpoints/tasks.py — HTTP endpoints for Task operations.

RESPONSIBILITY: Handle HTTP only.
  • Parse path params, query params, request bodies.
  • Call the service layer.
  • Return the right HTTP status code + response model.
  • Raise NO business exceptions — let the service do that.

Every function here is thin: 1–3 lines of real logic.
The heavy lifting is done by TaskService (services/task_service.py).

Routes exposed:
  GET    /api/v1/tasks            → list all tasks
  POST   /api/v1/tasks            → create a task
  GET    /api/v1/tasks/{task_id}  → get one task
  PUT    /api/v1/tasks/{task_id}  → update a task
  PATCH  /api/v1/tasks/{task_id}/toggle → toggle completed
  DELETE /api/v1/tasks/{task_id}  → delete a task
"""

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_task_service
from app.schemas.task import MessageResponse, TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

# APIRouter — mounted on /api/v1/tasks in api/v1/api.py
router = APIRouter()


# --------------------------------------------------------------------------- #
# List tasks
# --------------------------------------------------------------------------- #


@router.get(
    "/",
    response_model=list[TaskResponse],
    summary="List all tasks",
    description=(
        "Returns a paginated list of every task. "
        "Use `skip` and `limit` for pagination."
    ),
)
def list_tasks(
    skip: int = Query(default=0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Max tasks to return"),
    service: TaskService = Depends(get_task_service),
) -> list[TaskResponse]:
    return service.list_tasks(skip=skip, limit=limit)


# --------------------------------------------------------------------------- #
# Create task
# --------------------------------------------------------------------------- #


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,  # 201 = Created (more correct than 200)
    summary="Create a new task",
)
def create_task(
    body: TaskCreate,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    return service.create_task(body)


# --------------------------------------------------------------------------- #
# Get single task
# --------------------------------------------------------------------------- #


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID",
    responses={404: {"description": "Task not found"}},
)
def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    return service.get_task(task_id)


# --------------------------------------------------------------------------- #
# Update task
# --------------------------------------------------------------------------- #


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    description=(
        "Send only the fields you want to change. "
        "Unset fields keep their current values."
    ),
    responses={404: {"description": "Task not found"}},
)
def update_task(
    task_id: int,
    body: TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    return service.update_task(task_id, body)


# --------------------------------------------------------------------------- #
# Toggle completed
# --------------------------------------------------------------------------- #


@router.patch(
    "/{task_id}/toggle",
    response_model=TaskResponse,
    summary="Toggle task completion",
    description="Flips `completed` between true and false.",
    responses={404: {"description": "Task not found"}},
)
def toggle_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    return service.toggle_task(task_id)


# --------------------------------------------------------------------------- #
# Delete task
# --------------------------------------------------------------------------- #


@router.delete(
    "/{task_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a task",
    responses={404: {"description": "Task not found"}},
)
def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> MessageResponse:
    service.delete_task(task_id)
    return MessageResponse(message=f"Task {task_id} deleted successfully.")
