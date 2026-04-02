"""
tests/test_app.py
Pytest suite for ACEest Fitness & Gym Flask application.
Covers: routes, business logic, edge cases, and error handling.
"""

import pytest
from app import app, calculate_calories, clients, PROGRAMS


# ---------- Fixtures ----------
@pytest.fixture(autouse=True)
def clear_clients():
    """Reset in-memory client store before every test."""
    clients.clear()
    yield
    clients.clear()


@pytest.fixture
def client():
    """Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------- Unit tests: business logic ----------
class TestCalculateCalories:
    def test_fat_loss_program(self):
        assert calculate_calories(70, "Fat Loss") == 1540

    def test_muscle_gain_program(self):
        assert calculate_calories(80, "Muscle Gain") == 2800

    def test_beginner_program(self):
        assert calculate_calories(60, "Beginner") == 1560

    def test_unknown_program_returns_zero(self):
        assert calculate_calories(70, "Yoga") == 0

    def test_float_weight(self):
        result = calculate_calories(72.5, "Fat Loss")
        assert result == int(72.5 * 22)


# ---------- Integration tests: routes ----------
class TestIndexRoute:
    def test_index_returns_200(self, client):
        res = client.get("/")
        assert res.status_code == 200

    def test_index_contains_app_name(self, client):
        data = client.get("/").get_json()
        assert data["app"] == "ACEest Fitness & Gym"

    def test_index_status_running(self, client):
        data = client.get("/").get_json()
        assert data["status"] == "running"


class TestProgramsRoute:
    def test_get_programs_200(self, client):
        res = client.get("/programs")
        assert res.status_code == 200

    def test_get_programs_returns_list(self, client):
        data = client.get("/programs").get_json()
        assert "programs" in data
        assert isinstance(data["programs"], list)

    def test_all_programs_present(self, client):
        data = client.get("/programs").get_json()
        for p in PROGRAMS:
            assert p in data["programs"]


class TestAddClient:
    def _valid_payload(self):
        return {"name": "Arjun", "program": "Muscle Gain", "weight_kg": 75, "age": 28}

    def test_add_client_success(self, client):
        res = client.post("/clients", json=self._valid_payload())
        assert res.status_code == 201

    def test_add_client_returns_client_data(self, client):
        data = client.post("/clients", json=self._valid_payload()).get_json()
        assert data["client"]["name"] == "Arjun"
        assert data["client"]["program"] == "Muscle Gain"
        assert data["client"]["calories"] == calculate_calories(75, "Muscle Gain")

    def test_add_client_missing_name(self, client):
        res = client.post("/clients", json={"program": "Fat Loss", "weight_kg": 60})
        assert res.status_code == 400

    def test_add_client_invalid_program(self, client):
        res = client.post("/clients", json={"name": "Test", "program": "Zumba", "weight_kg": 60})
        assert res.status_code == 400

    def test_add_client_invalid_weight(self, client):
        res = client.post("/clients", json={"name": "Test", "program": "Beginner", "weight_kg": -5})
        assert res.status_code == 400

    def test_add_duplicate_client(self, client):
        payload = self._valid_payload()
        client.post("/clients", json=payload)
        res = client.post("/clients", json=payload)
        assert res.status_code == 409

    def test_add_client_no_body(self, client):
        res = client.post("/clients", content_type="application/json", data="")
        assert res.status_code == 400


class TestGetClients:
    def test_get_clients_empty(self, client):
        data = client.get("/clients").get_json()
        assert data["clients"] == []

    def test_get_clients_after_add(self, client):
        client.post("/clients", json={"name": "Priya", "program": "Fat Loss", "weight_kg": 55})
        data = client.get("/clients").get_json()
        assert len(data["clients"]) == 1

    def test_get_clients_multiple(self, client):
        client.post("/clients", json={"name": "A", "program": "Fat Loss", "weight_kg": 55})
        client.post("/clients", json={"name": "B", "program": "Beginner", "weight_kg": 65})
        data = client.get("/clients").get_json()
        assert len(data["clients"]) == 2


class TestGetSingleClient:
    def test_get_existing_client(self, client):
        client.post("/clients", json={"name": "Ravi", "program": "Beginner", "weight_kg": 65})
        res = client.get("/clients/Ravi")
        assert res.status_code == 200
        assert res.get_json()["name"] == "Ravi"

    def test_get_nonexistent_client(self, client):
        res = client.get("/clients/Ghost")
        assert res.status_code == 404


class TestDeleteClient:
    def test_delete_existing_client(self, client):
        client.post("/clients", json={"name": "Del", "program": "Fat Loss", "weight_kg": 60})
        res = client.delete("/clients/Del")
        assert res.status_code == 200

    def test_delete_removes_client(self, client):
        client.post("/clients", json={"name": "Del", "program": "Fat Loss", "weight_kg": 60})
        client.delete("/clients/Del")
        assert client.get("/clients/Del").status_code == 404

    def test_delete_nonexistent_client(self, client):
        res = client.delete("/clients/Nobody")
        assert res.status_code == 404


class TestProgressLogging:
    def test_log_valid_adherence(self, client):
        client.post("/clients", json={"name": "Sita", "program": "Fat Loss", "weight_kg": 58})
        res = client.post("/clients/Sita/progress", json={"adherence": 85})
        assert res.status_code == 200
        assert res.get_json()["adherence"] == 85

    def test_log_zero_adherence(self, client):
        client.post("/clients", json={"name": "Sita", "program": "Fat Loss", "weight_kg": 58})
        res = client.post("/clients/Sita/progress", json={"adherence": 0})
        assert res.status_code == 200

    def test_log_100_adherence(self, client):
        client.post("/clients", json={"name": "Sita", "program": "Fat Loss", "weight_kg": 58})
        res = client.post("/clients/Sita/progress", json={"adherence": 100})
        assert res.status_code == 200

    def test_log_invalid_adherence_above_100(self, client):
        client.post("/clients", json={"name": "Sita", "program": "Fat Loss", "weight_kg": 58})
        res = client.post("/clients/Sita/progress", json={"adherence": 150})
        assert res.status_code == 400

    def test_log_progress_unknown_client(self, client):
        res = client.post("/clients/Nobody/progress", json={"adherence": 80})
        assert res.status_code == 404


class TestCalorieCalculator:
    def test_calorie_endpoint_valid(self, client):
        res = client.get("/calories?weight=70&program=Fat+Loss")
        assert res.status_code == 200
        data = res.get_json()
        assert data["calories"] == 1540

    def test_calorie_endpoint_missing_weight(self, client):
        res = client.get("/calories?program=Fat+Loss")
        assert res.status_code == 400

    def test_calorie_endpoint_missing_program(self, client):
        res = client.get("/calories?weight=70")
        assert res.status_code == 400

    def test_calorie_endpoint_invalid_program(self, client):
        res = client.get("/calories?weight=70&program=Unknown")
        assert res.status_code == 400
