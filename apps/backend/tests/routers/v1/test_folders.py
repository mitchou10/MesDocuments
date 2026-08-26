import uuid

from app.db.models.enums import PermissionLevel, PrincipalType, ResourceType
from app.db.models.sharing import Share
from tests.routers.v1.conftest import client_as as _client_as


async def test_create_root_folder_and_it_appears_in_root_listing(db_session):
    user_id = uuid.uuid4()
    async with _client_as(db_session, user_id) as client:
        response = await client.post("/api/v1/folders", json={"name": "Clients"})
        assert response.status_code == 201
        folder_id = response.json()["id"]

        listing = await client.get("/api/v1/folders")
        assert listing.status_code == 200
        body = listing.json()
        assert body["total"] == 1
        assert [f["id"] for f in body["items"]] == [folder_id]


async def test_root_listing_only_shows_my_own_folders(db_session):
    alice = uuid.uuid4()
    bob = uuid.uuid4()
    async with _client_as(db_session, alice) as client:
        await client.post("/api/v1/folders", json={"name": "Alice's folder"})

    async with _client_as(db_session, bob) as client:
        bob_listing = await client.get("/api/v1/folders")

    assert bob_listing.json()["total"] == 0


async def test_get_folder_not_found(db_session):
    async with _client_as(db_session, uuid.uuid4()) as client:
        response = await client.get(f"/api/v1/folders/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_get_folder_denies_access_to_non_owner_without_share(db_session):
    owner = uuid.uuid4()
    stranger = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        created = await client.post("/api/v1/folders", json={"name": "Private"})
    folder_id = created.json()["id"]

    async with _client_as(db_session, stranger) as client:
        response = await client.get(f"/api/v1/folders/{folder_id}")

    assert response.status_code == 403


async def test_shared_folder_grants_reader_access(db_session):
    owner = uuid.uuid4()
    reader = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        created = await client.post("/api/v1/folders", json={"name": "Shared"})
    folder_id = created.json()["id"]

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
        response = await client.get(f"/api/v1/folders/{folder_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Shared"


async def test_reader_share_does_not_allow_creating_subfolders(db_session):
    owner = uuid.uuid4()
    reader = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        created = await client.post("/api/v1/folders", json={"name": "Shared"})
    folder_id = created.json()["id"]
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
        response = await client.post("/api/v1/folders", json={"name": "Subfolder", "parent_id": folder_id})

    assert response.status_code == 403


async def test_editor_share_allows_creating_subfolders(db_session):
    owner = uuid.uuid4()
    editor = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        created = await client.post("/api/v1/folders", json={"name": "Shared"})
    folder_id = created.json()["id"]
    db_session.add(
        Share(
            resource_type=ResourceType.folder,
            resource_id=uuid.UUID(folder_id),
            principal_type=PrincipalType.user,
            principal_id=editor,
            level=PermissionLevel.editor,
            created_by=owner,
        )
    )
    await db_session.commit()

    async with _client_as(db_session, editor) as client:
        response = await client.post("/api/v1/folders", json={"name": "Subfolder", "parent_id": folder_id})

    assert response.status_code == 201


async def test_access_to_a_folder_is_inherited_from_an_ancestor_share(db_session):
    owner = uuid.uuid4()
    reader = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        parent_id = (await client.post("/api/v1/folders", json={"name": "Clients"})).json()["id"]
        child_id = (
            await client.post("/api/v1/folders", json={"name": "ACME", "parent_id": parent_id})
        ).json()["id"]
    db_session.add(
        Share(
            resource_type=ResourceType.folder,
            resource_id=uuid.UUID(parent_id),
            principal_type=PrincipalType.user,
            principal_id=reader,
            level=PermissionLevel.reader,
            created_by=owner,
        )
    )
    await db_session.commit()

    async with _client_as(db_session, reader) as client:
        response = await client.get(f"/api/v1/folders/{child_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "ACME"


async def test_list_children(db_session):
    owner = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        parent_id = (await client.post("/api/v1/folders", json={"name": "Clients"})).json()["id"]
        await client.post("/api/v1/folders", json={"name": "ACME", "parent_id": parent_id})

        response = await client.get(f"/api/v1/folders/{parent_id}/children")

    assert response.status_code == 200
    body = response.json()
    assert [f["name"] for f in body["items"]] == ["ACME"]
    assert body["total"] == 1


async def test_rename_folder(db_session):
    owner = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        folder_id = (await client.post("/api/v1/folders", json={"name": "Clients"})).json()["id"]

        response = await client.patch(f"/api/v1/folders/{folder_id}", json={"name": "Clients (archive)"})

    assert response.status_code == 200
    assert response.json()["name"] == "Clients (archive)"


async def test_rename_folder_rejects_empty_name(db_session):
    owner = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        folder_id = (await client.post("/api/v1/folders", json={"name": "Clients"})).json()["id"]

        response = await client.patch(f"/api/v1/folders/{folder_id}", json={"name": "   "})

    assert response.status_code == 400


async def test_delete_folder_then_it_is_not_found(db_session):
    owner = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        folder_id = (await client.post("/api/v1/folders", json={"name": "Clients"})).json()["id"]

        delete_response = await client.delete(f"/api/v1/folders/{folder_id}")
        get_response = await client.get(f"/api/v1/folders/{folder_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
