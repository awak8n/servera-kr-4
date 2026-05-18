import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app import app, db_users, _id_seq, next_user_id
from itertools import count


@pytest.fixture(autouse=True)
def clear_db():
    """Очищает in-memory хранилище пользователей перед каждым тестом."""
    db_users.clear()
    import app as app_module
    app_module._id_seq = count(start=1)
    yield
    db_users.clear()


@pytest_asyncio.fixture
async def async_client():
    """Асинхронный HTTP-клиент через ASGITransport (без реального сервера)."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
