import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


class TestCustomExceptions:

    def test_create_product_negative_price_raises_422(self):
        """CustomExceptionA — цена <= 0."""
        payload = {"title": "Bad Item", "price": -5.0, "count": 1, "description": "test"}
        r = client.post("/products", json=payload)
        assert r.status_code == 422
        body = r.json()
        assert body["error_code"] == "BUSINESS_RULE_VIOLATED"
        assert "price" in body["detail"].lower()

    def test_get_nonexistent_product_raises_404(self):
        """CustomExceptionB — ресурс не найден."""
        r = client.get("/products/99999")
        assert r.status_code == 404
        body = r.json()
        assert body["error_code"] == "RESOURCE_NOT_FOUND"

    def test_buy_insufficient_stock_raises_409(self):
        """InsufficientStockException — нехватка товара."""
        create_r = client.post(
            "/products",
            json={"title": "Widget", "price": 9.99, "count": 2, "description": "small widget"},
        )
        pid = create_r.json()["id"]
        r = client.post(f"/products/{pid}/buy?quantity=100")
        assert r.status_code == 409
        assert r.json()["error_code"] == "INSUFFICIENT_STOCK"

    def test_error_response_has_required_fields(self):
        r = client.get("/products/99999")
        body = r.json()
        for key in ("error_code", "message", "detail"):
            assert key in body, f"Missing key: {key}"
