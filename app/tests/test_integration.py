"""
tests/test_integration.py — Integration tests for API endpoints.

WHAT is an integration test?
  We test the FULL stack from HTTP request → DB and back.
  We use FastAPI's TestClient (from Starlette) which simulates real HTTP
  calls without starting a real server.

WHAT do we test here?
  • Correct status codes (200, 201, 404, 422 for validation errors).
  • Correct JSON response shape.
  • Each endpoint in isolation.

Run with:
    uv run pytest app/tests/test_integration.py -v
"""

from fastapi.testclient import TestClient

# =========================================================================== #
# /health
# =========================================================================== #


class TestHealth:
    def test_health_returns_ok(self, client: TestClient) -> None:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"


# =========================================================================== #
# POST /api/v1/tasks
# =========================================================================== #


class TestCreateTask:
    def test_create_task_returns_201(self, client: TestClient) -> None:
        """Creating a valid task returns HTTP 201 Created."""
        payload = {"title": "Buy groceries", "description": "Milk and eggs"}

        response = client.post("/api/v1/tasks/", json=payload)

        assert response.status_code == 201

    def test_create_task_response_shape(self, client: TestClient) -> None:
        """Response body must contain all expected fields."""
        response = client.post("/api/v1/tasks/", json={"title": "Test task"})
        body = response.json()

        assert "id" in body
        assert "title" in body
        assert "completed" in body
        assert "created_at" in body
        assert "updated_at" in body

    def test_create_task_completed_defaults_false(self, client: TestClient) -> None:
        """A newly created task must not be completed."""
        response = client.post("/api/v1/tasks/", json={"title": "New task"})

        assert response.json()["completed"] is False

    def test_create_task_missing_title_returns_422(self, client: TestClient) -> None:
        """Sending an empty body should return HTTP 422 Unprocessable Entity."""
        response = client.post("/api/v1/tasks/", json={})

        assert response.status_code == 422

    def test_create_task_empty_title_returns_422(self, client: TestClient) -> None:
        """An empty string title should fail Pydantic's min_length=1 rule."""
        response = client.post("/api/v1/tasks/", json={"title": ""})

        assert response.status_code == 422


# =========================================================================== #
# GET /api/v1/tasks
# =========================================================================== #


class TestListTasks:
    def test_list_tasks_returns_200(self, client: TestClient) -> None:
        response = client.get("/api/v1/tasks/")

        assert response.status_code == 200

    def test_list_tasks_returns_list(self, client: TestClient) -> None:
        """Response must be a JSON array."""
        response = client.get("/api/v1/tasks/")

        assert isinstance(response.json(), list)

    def test_list_tasks_shows_created_tasks(self, client: TestClient) -> None:
        """Tasks created via POST must appear in the list."""
        client.post("/api/v1/tasks/", json={"title": "Alpha"})
        client.post("/api/v1/tasks/", json={"title": "Beta"})

        response = client.get("/api/v1/tasks/")
        titles = [t["title"] for t in response.json()]

        assert "Alpha" in titles
        assert "Beta" in titles

    def test_list_tasks_pagination(self, client: TestClient) -> None:
        """limit query param should restrict the number of returned rows."""
        for i in range(5):
            client.post("/api/v1/tasks/", json={"title": f"Task {i}"})

        response = client.get("/api/v1/tasks/?skip=0&limit=2")

        assert len(response.json()) == 2


# =========================================================================== #
# GET /api/v1/tasks/{id}
# =========================================================================== #


class TestGetTask:
    def test_get_existing_task_returns_200(self, client: TestClient) -> None:
        created = client.post("/api/v1/tasks/", json={"title": "My task"}).json()

        response = client.get(f"/api/v1/tasks/{created['id']}")

        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_get_missing_task_returns_404(self, client: TestClient) -> None:
        response = client.get("/api/v1/tasks/99999")

        assert response.status_code == 404


# =========================================================================== #
# PUT /api/v1/tasks/{id}
# =========================================================================== #


class TestUpdateTask:
    def test_update_task_title(self, client: TestClient) -> None:
        """PUT with a new title should update only the title."""
        created = client.post("/api/v1/tasks/", json={"title": "Old title"}).json()

        response = client.put(
            f"/api/v1/tasks/{created['id']}", json={"title": "New title"}
        )

        assert response.status_code == 200
        assert response.json()["title"] == "New title"

    def test_update_missing_task_returns_404(self, client: TestClient) -> None:
        response = client.put("/api/v1/tasks/99999", json={"title": "Ghost"})

        assert response.status_code == 404


# =========================================================================== #
# PATCH /api/v1/tasks/{id}/toggle
# =========================================================================== #


class TestToggleTask:
    def test_toggle_marks_task_complete(self, client: TestClient) -> None:
        """First toggle on a new task should set completed=True."""
        created = client.post("/api/v1/tasks/", json={"title": "Toggle me"}).json()
        assert created["completed"] is False

        response = client.patch(f"/api/v1/tasks/{created['id']}/toggle")

        assert response.status_code == 200
        assert response.json()["completed"] is True

    def test_toggle_twice_returns_to_false(self, client: TestClient) -> None:
        """Toggling twice should return completed=False."""
        created = client.post("/api/v1/tasks/", json={"title": "Double toggle"}).json()
        task_id = created["id"]

        client.patch(f"/api/v1/tasks/{task_id}/toggle")  # → True
        response = client.patch(f"/api/v1/tasks/{task_id}/toggle")  # → False

        assert response.json()["completed"] is False

    def test_toggle_missing_task_returns_404(self, client: TestClient) -> None:
        response = client.patch("/api/v1/tasks/99999/toggle")

        assert response.status_code == 404


# =========================================================================== #
# DELETE /api/v1/tasks/{id}
# =========================================================================== #


class TestDeleteTask:
    def test_delete_task_returns_200(self, client: TestClient) -> None:
        created = client.post("/api/v1/tasks/", json={"title": "Gone"}).json()

        response = client.delete(f"/api/v1/tasks/{created['id']}")

        assert response.status_code == 200

    def test_delete_task_removes_it(self, client: TestClient) -> None:
        """After DELETE, GET on the same ID should return 404."""
        created = client.post("/api/v1/tasks/", json={"title": "Temporary"}).json()
        task_id = created["id"]

        client.delete(f"/api/v1/tasks/{task_id}")

        response = client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 404

    def test_delete_missing_task_returns_404(self, client: TestClient) -> None:
        response = client.delete("/api/v1/tasks/99999")

        assert response.status_code == 404
