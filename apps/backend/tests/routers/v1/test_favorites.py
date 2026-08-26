import uuid

from app.db.models.enums import PermissionLevel, PrincipalType, ResourceType
from app.db.models.sharing import Share
from tests.routers.v1.conftest import client_as as _client_as


async def test_toggle_favorite_adds_then_removes(db_session):
    owner = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        folder_id = (await client.post("/api/v1/folders", json={"name": "Clients"})).json()["id"]

        first = await client.post(f"/api/v1/folders/{folder_id}/favorite")
        second = await client.post(f"/api/v1/folders/{folder_id}/favorite")

    assert first.status_code == 200
    assert first.json() == {"favorited": True}
    assert second.json() == {"favorited": False}


async def test_toggle_favorite_requires_at_least_reader_access(db_session):
    owner = uuid.uuid4()
    stranger = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        folder_id = (await client.post("/api/v1/folders", json={"name": "Private"})).json()["id"]

    async with _client_as(db_session, stranger) as client:
        response = await client.post(f"/api/v1/folders/{folder_id}/favorite")

    assert response.status_code == 403


async def test_toggle_favorite_on_unknown_folder_is_404(db_session):
    owner = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        response = await client.post(f"/api/v1/folders/{uuid.uuid4()}/favorite")

    assert response.status_code == 404


async def test_reader_share_is_enough_to_favorite(db_session):
    owner = uuid.uuid4()
    reader = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        folder_id = (await client.post("/api/v1/folders", json={"name": "Shared"})).json()["id"]

    db_session.add(
        Share(
            resource_type=ResourceType.folder,
            resource_id=uuid.UUID(folder_id),
            principal_type=PrincipalType.user,
            principal_id=reader,
            level=PermissionLevel.reader,
            created_by=owner,
        )
    )
    await db_session.commit()

    async with _client_as(db_session, reader) as client:
        response = await client.post(f"/api/v1/folders/{folder_id}/favorite")

    assert response.status_code == 200
    assert response.json() == {"favorited": True}


async def test_list_favorite_folders(db_session):
    owner = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        folder_id = (await client.post("/api/v1/folders", json={"name": "Clients"})).json()["id"]
        await client.post("/api/v1/folders", json={"name": "Not favorited"})
        await client.post(f"/api/v1/folders/{folder_id}/favorite")

        response = await client.get("/api/v1/favorites/folders")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert [f["id"] for f in body["items"]] == [folder_id]


async def test_list_favorite_folders_is_scoped_per_user(db_session):
    owner = uuid.uuid4()
    other = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        folder_id = (await client.post("/api/v1/folders", json={"name": "Clients"})).json()["id"]
        await client.post(f"/api/v1/folders/{folder_id}/favorite")

    async with _client_as(db_session, other) as client:
        response = await client.get("/api/v1/favorites/folders")

    assert response.json()["total"] == 0
