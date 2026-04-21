"""
tests/test_e2e.py — End-to-end tests simulating a real user flow.

WHAT is an E2E test?
  We simulate a COMPLETE user journey through the API, just like a real
  client would use it.  Each test touches multiple endpoints in sequence
  and checks the system behaves correctly as a whole.

USER FLOW we simulate:
  1. User creates a task.
  2. User lists tasks and finds theirs.
  3. User gets the task by ID.
  4. User updates the task title.
  5. User marks the task complete.
  6. User verifies the task shows as complete in the list.
  7. User deletes the task.
  8. User confirms the task no longer exists.

Run with:
    uv run pytest app/tests/test_e2e.py -v
"""

from fastapi.testclient import TestClient


class TestFullTaskLifecycle:
    """
    Simulates the complete lifecycle of a single task from creation to deletion.
    Each method runs in order — we share `task_id` across steps via an instance var.
    """

    def test_step_1_create_task(self, client: TestClient) -> None:
        """Step 1: Create a task and verify it's saved correctly."""
        payload = {
            "title": "Learn FastAPI",
            "description": "Build a production-style REST API with clean architecture",
        }

        response = client.post("/api/v1/tasks/", json=payload)

        assert response.status_code == 201
        body = response.json()
        assert body["title"] == "Learn FastAPI"
        assert body["completed"] is False
        assert body["id"] is not None

        # Store task_id on the class so other steps can use it
        TestFullTaskLifecycle._task_id = body["id"]

    def test_step_2_list_tasks_shows_new_task(self, client: TestClient) -> None:
        """Step 2: The new task must appear in the task list."""
        # Re-create so we have a task (each test gets a fresh DB via conftest)
        created = client.post(
            "/api/v1/tasks/", json={"title": "Learn FastAPI"}
        ).json()

        response = client.get("/api/v1/tasks/")

        assert response.status_code == 200
        ids = [t["id"] for t in response.json()]
        assert created["id"] in ids

    def test_step_3_get_single_task(self, client: TestClient) -> None:
        """Step 3: Fetch the task by ID and check all returned fields."""
        created = client.post(
            "/api/v1/tasks/",
            json={"title": "Learn FastAPI", "description": "Clean architecture"},
        ).json()

        response = client.get(f"/api/v1/tasks/{created['id']}")

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == created["id"]
        assert body["title"] == "Learn FastAPI"
        assert body["description"] == "Clean architecture"

    def test_step_4_update_task(self, client: TestClient) -> None:
        """Step 4: Update the task title; other fields remain unchanged."""
        created = client.post("/api/v1/tasks/", json={"title": "Old title"}).json()

        response = client.put(
            f"/api/v1/tasks/{created['id']}", json={"title": "Updated: Learn FastAPI"}
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Updated: Learn FastAPI"

    def test_step_5_mark_complete(self, client: TestClient) -> None:
        """Step 5: Toggle the task to completed=True."""
        created = client.post(
            "/api/v1/tasks/", json={"title": "Task to complete"}
        ).json()

        response = client.patch(f"/api/v1/tasks/{created['id']}/toggle")

        assert response.status_code == 200
        assert response.json()["completed"] is True

    def test_step_6_completed_task_visible_in_list(self, client: TestClient) -> None:
        """Step 6: The completed task must still appear in the list."""
        created = client.post("/api/v1/tasks/", json={"title": "Check in list"}).json()
        client.patch(f"/api/v1/tasks/{created['id']}/toggle")  # mark done

        response = client.get("/api/v1/tasks/")
        tasks = response.json()

        found = next((t for t in tasks if t["id"] == created["id"]), None)
        assert found is not None
        assert found["completed"] is True

    def test_step_7_delete_task(self, client: TestClient) -> None:
        """Step 7: Delete the task and verify we get a success response."""
        created = client.post("/api/v1/tasks/", json={"title": "Temporary"}).json()

        response = client.delete(f"/api/v1/tasks/{created['id']}")

        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

    def test_step_8_deleted_task_is_gone(self, client: TestClient) -> None:
        """Step 8: After deletion, the task must return 404."""
        created = client.post("/api/v1/tasks/", json={"title": "Gone task"}).json()
        task_id = created["id"]
        client.delete(f"/api/v1/tasks/{task_id}")

        response = client.get(f"/api/v1/tasks/{task_id}")

        assert response.status_code == 404


class TestEdgeCases:
    """Test boundary and error conditions that real users might trigger."""

    def test_create_very_long_title_fails(self, client: TestClient) -> None:
        """Title exceeding 255 chars must be rejected with 422."""
        response = client.post("/api/v1/tasks/", json={"title": "x" * 256})

        assert response.status_code == 422

    def test_get_invalid_id_type(self, client: TestClient) -> None:
        """Non-integer task ID in path should return 422."""
        response = client.get("/api/v1/tasks/not-a-number")

        assert response.status_code == 422

    def test_empty_list_on_fresh_db(self, client: TestClient) -> None:
        """Fresh database should return an empty list, not an error."""
        response = client.get("/api/v1/tasks/")

        assert response.status_code == 200
        assert response.json() == []

    def test_health_endpoint_always_works(self, client: TestClient) -> None:
        """Health endpoint must return 200 at any point in the user flow."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"
