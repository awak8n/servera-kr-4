import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

VALID_USER = {
    "username": "john_doe",
    "age": 25,
    "email": "john@example.com",
    "password": "securepass",
    "phone": "+7-999-000-00-00",
}


class TestUserValidation:

    def test_valid_user_returns_201(self):
        r = client.post("/users/validate", json=VALID_USER)
        assert r.status_code == 201

    def test_valid_user_without_optional_phone(self):
        payload = {**VALID_USER}
        del payload["phone"]
        r = client.post("/users/validate", json=payload)
        assert r.status_code == 201
        assert r.json()["data"]["phone"] == "Unknown"

    def test_age_too_young_returns_422(self):
        """age должен быть > 18."""
        r = client.post("/users/validate", json={**VALID_USER, "age": 16})
        assert r.status_code == 422
        body = r.json()
        assert body["error_code"] == "VALIDATION_ERROR"

    def test_age_exactly_18_returns_422(self):
        """age=18 не проходит (gt=18 означает строго больше)."""
        r = client.post("/users/validate", json={**VALID_USER, "age": 18})
        assert r.status_code == 422

    def test_invalid_email_returns_422(self):
        r = client.post("/users/validate", json={**VALID_USER, "email": "not-an-email"})
        assert r.status_code == 422

    def test_password_too_short_returns_422(self):
        r = client.post("/users/validate", json={**VALID_USER, "password": "short"})
        assert r.status_code == 422

    def test_password_too_long_returns_422(self):
        r = client.post("/users/validate", json={**VALID_USER, "password": "a" * 17})
        assert r.status_code == 422

    def test_validation_error_contains_errors_list(self):
        r = client.post("/users/validate", json={**VALID_USER, "age": 10, "email": "bad"})
        body = r.json()
        assert "errors" in body
        assert isinstance(body["errors"], list)
        assert len(body["errors"]) >= 2
