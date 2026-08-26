import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.main import app
from app.schemas.auth import CurrentUser


def client_as(db_session, user_id: uuid.UUID, **claims) -> AsyncClient:
    # A plain TestClient runs the ASGI app in its own thread/event loop, which
    # can't share an asyncpg-backed AsyncSession created in *this* test's loop
    # ("attached to a different loop"). ASGITransport calls the app in-process
    # on the current loop instead, so the same `db_session` works on both
    # sides of the request.
    async def override_get_db():
        yield db_session

    def override_get_current_user() -> CurrentUser:
        return CurrentUser(
            sub=str(user_id),
            username=claims.get("username", "camille"),
            email=claims.get("email", "camille@example.fr"),
            name=claims.get("name", "Camille Bernard"),
            roles=["user"],
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()
