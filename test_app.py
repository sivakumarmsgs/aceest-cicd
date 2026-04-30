"""
ACEest Fitness & Gym - Pytest Test Suite
Task 3: Unit Testing and Test Automation
Tests cover: health check, client CRUD, workouts, metrics, programs, login
"""

import pytest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, init_db, DB_NAME

TEST_DB = "test_aceest.db"


@pytest.fixture(scope="module")
def client():
    """Set up Flask test client with isolated test database."""
    import app as app_module
    app_module.DB_NAME = TEST_DB
    app.config["TESTING"] = True
    init_db(TEST_DB)
    with app.test_client() as test_client:
        yield test_client
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


# ============================================================
# Task 1: Health & Version Endpoints
# ============================================================

class TestHealthAndVersion:
    def test_index_returns_200(self, client):
        """Test root endpoint returns 200 with app info."""
        response = client.get("/")
        assert response.status_code == 200

    def test_index_contains_app_name(self, client):
        """Test root endpoint returns correct app name."""
        response = client.get("/")
        data = json.loads(response.data)
        assert data["app"] == "ACEest Fitness & Gym"

    def test_health_endpoint_returns_healthy(self, client):
        """Test /health returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"

    def test_version_endpoint(self, client):
        """Test /version returns version string."""
        response = client.get("/version")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "version" in data
        assert data["version"] == "3.2.4"


# ============================================================
# Task 2: Client Management
# ============================================================

class TestClientManagement:
    def test_get_clients_empty(self, client):
        """Test GET /clients returns list (may be empty initially)."""
        response = client.get("/clients")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_add_client_success(self, client):
        """Test adding a new client successfully."""
        payload = {
            "name": "John Doe",
            "age": 28,
            "weight": 80.5,
            "height": 175.0,
            "program": "Fat Loss",
            "calories": 2200
        }
        response = client.post("/clients", json=payload)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["message"] == "Client added successfully"
        assert data["name"] == "John Doe"

    def test_add_client_missing_field(self, client):
        """Test adding client with missing required field returns 400."""
        payload = {"name": "Incomplete Client"}
        response = client.post("/clients", json=payload)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_add_duplicate_client_returns_409(self, client):
        """Test adding duplicate client returns 409."""
        payload = {"name": "John Doe", "age": 28, "weight": 80.5, "height": 175.0}
        response = client.post("/clients", json=payload)
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data["error"] == "Client already exists"

    def test_get_client_by_name(self, client):
        """Test retrieving a specific client by name."""
        response = client.get("/clients/John Doe")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "John Doe"
        assert data["age"] == 28

    def test_get_nonexistent_client_returns_404(self, client):
        """Test retrieving non-existent client returns 404."""
        response = client.get("/clients/Ghost User")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data

    def test_add_second_client(self, client):
        """Test adding another client successfully."""
        payload = {
            "name": "Jane Smith",
            "age": 32,
            "weight": 65.0,
            "height": 162.0,
            "program": "Muscle Gain",
            "calories": 2800,
            "membership_status": "Active"
        }
        response = client.post("/clients", json=payload)
        assert response.status_code == 201

    def test_get_all_clients_returns_multiple(self, client):
        """Test GET /clients returns multiple clients."""
        response = client.get("/clients")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 2

    def test_delete_client(self, client):
        """Test deleting a client."""
        response = client.delete("/clients/Jane Smith")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "deleted" in data["message"]

    def test_deleted_client_not_found(self, client):
        """Test deleted client returns 404."""
        response = client.get("/clients/Jane Smith")
        assert response.status_code == 404

    def test_add_client_no_body_returns_400(self, client):
        """Test POST /clients with no body returns 400."""
        response = client.post("/clients", data="", content_type="application/json")
        assert response.status_code == 400


# ============================================================
# Task 3: Workout Logging
# ============================================================

class TestWorkoutLogging:
    def test_get_workouts_returns_list(self, client):
        """Test GET /workouts returns list."""
        response = client.get("/workouts")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_add_workout_success(self, client):
        """Test adding a workout successfully."""
        payload = {
            "client_name": "John Doe",
            "workout_type": "Strength",
            "duration_min": 60,
            "date": "2025-01-15",
            "notes": "Heavy squat day"
        }
        response = client.post("/workouts", json=payload)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert "successfully" in data["message"]

    def test_add_workout_missing_field(self, client):
        """Test adding workout with missing field returns 400."""
        payload = {"client_name": "John Doe"}
        response = client.post("/workouts", json=payload)
        assert response.status_code == 400

    def test_add_multiple_workouts(self, client):
        """Test logging multiple workouts."""
        workouts = [
            {"client_name": "John Doe", "workout_type": "Cardio", "duration_min": 45},
            {"client_name": "John Doe", "workout_type": "Hypertrophy", "duration_min": 75},
        ]
        for w in workouts:
            response = client.post("/workouts", json=w)
            assert response.status_code == 201

    def test_get_workouts_after_adding(self, client):
        """Test workouts list grows after adding."""
        response = client.get("/workouts")
        data = json.loads(response.data)
        assert len(data) >= 3

    def test_add_workout_no_body(self, client):
        """Test POST /workouts with no body returns 400."""
        response = client.post("/workouts", data="", content_type="application/json")
        assert response.status_code == 400


# ============================================================
# Task 4: Metrics Tracking
# ============================================================

class TestMetricsTracking:
    def test_add_metrics_success(self, client):
        """Test adding metrics for a client."""
        payload = {
            "client_name": "John Doe",
            "date": "2025-01-15",
            "weight": 79.5,
            "waist": 85.0,
            "bodyfat": 18.5
        }
        response = client.post("/metrics", json=payload)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["message"] == "Metrics saved"

    def test_add_metrics_missing_client(self, client):
        """Test adding metrics without client_name returns 400."""
        payload = {"weight": 80.0}
        response = client.post("/metrics", json=payload)
        assert response.status_code == 400

    def test_add_metrics_no_body(self, client):
        """Test POST /metrics with no body returns 400."""
        response = client.post("/metrics", data="", content_type="application/json")
        assert response.status_code == 400


# ============================================================
# Task 5: Program Recommendations
# ============================================================

class TestProgramRecommendations:
    def test_get_programs_returns_dict(self, client):
        """Test GET /programs returns dictionary of programs."""
        response = client.get("/programs")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, dict)

    def test_programs_contains_fat_loss(self, client):
        """Test programs include Fat Loss category."""
        response = client.get("/programs")
        data = json.loads(response.data)
        assert "Fat Loss" in data

    def test_programs_contains_muscle_gain(self, client):
        """Test programs include Muscle Gain category."""
        response = client.get("/programs")
        data = json.loads(response.data)
        assert "Muscle Gain" in data

    def test_programs_contains_beginner(self, client):
        """Test programs include Beginner category."""
        response = client.get("/programs")
        data = json.loads(response.data)
        assert "Beginner" in data

    def test_programs_have_lists(self, client):
        """Test each program category has list of workouts."""
        response = client.get("/programs")
        data = json.loads(response.data)
        for key, value in data.items():
            assert isinstance(value, list)
            assert len(value) > 0


# ============================================================
# Task 6: Authentication
# ============================================================

class TestAuthentication:
    def test_valid_login(self, client):
        """Test valid admin login returns 200."""
        response = client.post("/login", json={"username": "admin", "password": "admin123"})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Login successful"
        assert data["role"] == "Admin"

    def test_invalid_login(self, client):
        """Test invalid credentials returns 401."""
        response = client.post("/login", json={"username": "admin", "password": "wrongpass"})
        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data

    def test_login_no_body(self, client):
        """Test login with no body returns 400."""
        response = client.post("/login", data="", content_type="application/json")
        assert response.status_code == 400

    def test_login_wrong_username(self, client):
        """Test login with wrong username returns 401."""
        response = client.post("/login", json={"username": "hacker", "password": "admin123"})
        assert response.status_code == 401


# ============================================================
# Task 7: Data Validation
# ============================================================

class TestDataValidation:
    def test_client_age_stored_as_integer(self, client):
        """Test client age is stored correctly as integer."""
        client.post("/clients", json={
            "name": "ValidAge Client", "age": 25, "weight": 70.0, "height": 170.0
        })
        response = client.get("/clients/ValidAge Client")
        data = json.loads(response.data)
        assert data["age"] == 25
        assert isinstance(data["age"], int)

    def test_client_weight_stored_as_float(self, client):
        """Test client weight is stored correctly as float."""
        response = client.get("/clients/John Doe")
        data = json.loads(response.data)
        assert isinstance(data["weight"], float)

    def test_client_default_membership_status(self, client):
        """Test new client gets Active membership by default."""
        response = client.get("/clients/John Doe")
        data = json.loads(response.data)
        assert data["membership_status"] == "Active"

    def test_client_default_calories(self, client):
        """Test client with no calories gets default 2000."""
        client.post("/clients", json={
            "name": "Default Calories", "age": 30, "weight": 75.0, "height": 178.0
        })
        response = client.get("/clients/Default Calories")
        data = json.loads(response.data)
        assert data["calories"] == 2000
