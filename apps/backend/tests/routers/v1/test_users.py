import uuid

from tests.routers.v1.conftest import client_as as _client_as


async def test_search_finds_matching_user(db_session, make_user):
    searcher = uuid.uuid4()
    await make_user(id=uuid.uuid4(), username="bob.martin", email="bob@example.fr", display_name="Bob Martin")

    async with _client_as(db_session, searcher) as client:
        response = await client.get("/api/v1/users/search", params={"q": "martin"})

    assert response.status_code == 200
    body = response.json()
    assert [u["username"] for u in body] == ["bob.martin"]


async def test_search_requires_authentication():
    from httpx import ASGITransport, AsyncClient

    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/users/search", params={"q": "martin"})

    assert response.status_code in (401, 403)


async def test_search_returns_empty_list_when_no_match(db_session):
    searcher = uuid.uuid4()
    async with _client_as(db_session, searcher) as client:
        response = await client.get("/api/v1/users/search", params={"q": "nonexistent"})

    assert response.status_code == 200
    assert response.json() == []


async def test_get_user_by_id(db_session, make_user):
    searcher = uuid.uuid4()
    other = await make_user(id=uuid.uuid4(), username="bob.martin", email="bob@example.fr")

    async with _client_as(db_session, searcher) as client:
        response = await client.get(f"/api/v1/users/{other.id}")

    assert response.status_code == 200
    assert response.json()["username"] == "bob.martin"


async def test_get_user_by_id_not_found(db_session):
    searcher = uuid.uuid4()
    async with _client_as(db_session, searcher) as client:
        response = await client.get(f"/api/v1/users/{uuid.uuid4()}")

    assert response.status_code == 404
