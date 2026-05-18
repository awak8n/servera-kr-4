import pytest
from faker import Faker

fake = Faker()

pytestmark = pytest.mark.asyncio


# Вспомогательные функции
def make_user_payload() -> dict:
    return {
        "username": fake.user_name(),
        "age": fake.random_int(min=1, max=99),
    }


# POST /users — создание пользователя
class TestCreateUser:

    async def test_create_user_returns_201(self, async_client):
        payload = make_user_payload()
        response = await async_client.post("/users", json=payload)
        assert response.status_code == 201

    async def test_create_user_response_structure(self, async_client):
        payload = make_user_payload()
        response = await async_client.post("/users", json=payload)
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "age" in data
        assert isinstance(data["id"], int)

    async def test_create_user_returns_correct_data(self, async_client):
        payload = make_user_payload()
        response = await async_client.post("/users", json=payload)
        data = response.json()
        assert data["username"] == payload["username"]
        assert data["age"] == payload["age"]

    async def test_create_multiple_users_unique_ids(self, async_client):
        ids = []
        for _ in range(3):
            r = await async_client.post("/users", json=make_user_payload())
            ids.append(r.json()["id"])
        assert len(set(ids)) == 3, "IDs must be unique"

    async def test_create_user_missing_field_returns_422(self, async_client):
        response = await async_client.post("/users", json={"username": "only_name"})
        assert response.status_code == 422

    async def test_create_user_empty_body_returns_422(self, async_client):
        response = await async_client.post("/users", json={})
        assert response.status_code == 422


# GET /users/{user_id} — получение пользователя
class TestGetUser:

    async def test_get_existing_user_returns_200(self, async_client):
        payload = make_user_payload()
        create_r = await async_client.post("/users", json=payload)
        user_id = create_r.json()["id"]

        response = await async_client.get(f"/users/{user_id}")
        assert response.status_code == 200

    async def test_get_existing_user_correct_data(self, async_client):
        payload = make_user_payload()
        create_r = await async_client.post("/users", json=payload)
        user_id = create_r.json()["id"]

        response = await async_client.get(f"/users/{user_id}")
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == payload["username"]
        assert data["age"] == payload["age"]

    async def test_get_nonexistent_user_returns_404(self, async_client):
        response = await async_client.get("/users/99999")
        assert response.status_code == 404

    async def test_get_nonexistent_user_error_message(self, async_client):
        response = await async_client.get("/users/99999")
        assert "not found" in response.json()["detail"].lower()

    async def test_get_user_after_different_user_created(self, async_client):
        """Проверяем, что получаем именно того пользователя."""
        p1 = {"username": fake.user_name(), "age": 25}
        p2 = {"username": fake.user_name(), "age": 30}
        r1 = await async_client.post("/users", json=p1)
        r2 = await async_client.post("/users", json=p2)

        response = await async_client.get(f"/users/{r1.json()['id']}")
        assert response.json()["username"] == p1["username"]

        response = await async_client.get(f"/users/{r2.json()['id']}")
        assert response.json()["username"] == p2["username"]


# DELETE /users/{user_id} — удаление пользователя
class TestDeleteUser:

    async def test_delete_existing_user_returns_204(self, async_client):
        create_r = await async_client.post("/users", json=make_user_payload())
        user_id = create_r.json()["id"]

        response = await async_client.delete(f"/users/{user_id}")
        assert response.status_code == 204

    async def test_delete_removes_user(self, async_client):
        create_r = await async_client.post("/users", json=make_user_payload())
        user_id = create_r.json()["id"]

        await async_client.delete(f"/users/{user_id}")
        get_r = await async_client.get(f"/users/{user_id}")
        assert get_r.status_code == 404

    async def test_delete_nonexistent_user_returns_404(self, async_client):
        response = await async_client.delete("/users/99999")
        assert response.status_code == 404

    async def test_double_delete_returns_404(self, async_client):
        """Повторное удаление того же пользователя → 404."""
        create_r = await async_client.post("/users", json=make_user_payload())
        user_id = create_r.json()["id"]

        first = await async_client.delete(f"/users/{user_id}")
        assert first.status_code == 204

        second = await async_client.delete(f"/users/{user_id}")
        assert second.status_code == 404

    async def test_delete_does_not_affect_other_users(self, async_client):
        r1 = await async_client.post("/users", json=make_user_payload())
        r2 = await async_client.post("/users", json=make_user_payload())
        id1, id2 = r1.json()["id"], r2.json()["id"]

        await async_client.delete(f"/users/{id1}")
        assert (await async_client.get(f"/users/{id2}")).status_code == 200


# Изоляция состояния
class TestStateIsolation:

    async def test_db_is_empty_at_start(self, async_client):
        """После очистки в conftest хранилище пустое."""
        from app import db_users
        assert len(db_users) == 0

    async def test_created_user_exists_only_in_this_test(self, async_client):
        await async_client.post("/users", json=make_user_payload())
        from app import db_users
        assert len(db_users) == 1  # только один, не накапливается
