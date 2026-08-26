import uuid

from tests.routers.v1.conftest import client_as as _client_as


async def test_add_and_list_folder_shares(db_session):
    owner = uuid.uuid4()
    reader = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        folder_id = (await client.post("/api/v1/folders", json={"name": "Clients"})).json()["id"]

        add_response = await client.post(
            f"/api/v1/folders/{folder_id}/shares",
            json={
                "resource_type": "folder",
                "resource_id": folder_id,
                "principal_type": "user",
                "principal_id": str(reader),
                "level": "reader",
            },
        )
        assert add_response.status_code == 201
        assert add_response.json()["principal_id"] == str(reader)

        list_response = await client.get(f"/api/v1/folders/{folder_id}/shares")

    assert list_response.status_code == 200
    body = list_response.json()
    assert len(body) == 1
    assert body[0]["level"] == "reader"


async def test_add_share_rejects_mismatched_resource(db_session):
    owner = uuid.uuid4()
    other_folder_id = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        folder_id = (await client.post("/api/v1/folders", json={"name": "Clients"})).json()["id"]

        response = await client.post(
            f"/api/v1/folders/{folder_id}/shares",
            json={
                "resource_type": "folder",
                "resource_id": str(other_folder_id),
                "principal_type": "user",
                "principal_id": str(uuid.uuid4()),
                "level": "reader",
            },
        )

    assert response.status_code == 400


async def test_add_share_requires_editor_access(db_session):
    owner = uuid.uuid4()
    stranger = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        folder_id = (await client.post("/api/v1/folders", json={"name": "Private"})).json()["id"]

    async with _client_as(db_session, stranger) as client:
        response = await client.post(
            f"/api/v1/folders/{folder_id}/shares",
            json={
                "resource_type": "folder",
                "resource_id": folder_id,
                "principal_type": "user",
                "principal_id": str(uuid.uuid4()),
                "level": "reader",
            },
        )

    assert response.status_code == 403


async def test_add_share_on_unknown_folder_is_404(db_session):
    owner = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        folder_id = uuid.uuid4()
        response = await client.post(
            f"/api/v1/folders/{folder_id}/shares",
            json={
                "resource_type": "folder",
                "resource_id": str(folder_id),
                "principal_type": "user",
                "principal_id": str(uuid.uuid4()),
                "level": "reader",
            },
        )

    assert response.status_code == 404


async def test_remove_share(db_session):
    owner = uuid.uuid4()
    reader = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        folder_id = (await client.post("/api/v1/folders", json={"name": "Clients"})).json()["id"]
        share_id = (
            await client.post(
                f"/api/v1/folders/{folder_id}/shares",
                json={
                    "resource_type": "folder",
                    "resource_id": folder_id,
                    "principal_type": "user",
                    "principal_id": str(reader),
                    "level": "reader",
                },
            )
        ).json()["id"]

        delete_response = await client.delete(f"/api/v1/shares/{share_id}")
        list_response = await client.get(f"/api/v1/folders/{folder_id}/shares")

    assert delete_response.status_code == 204
    assert list_response.json() == []


async def test_remove_share_requires_editor_access_on_the_underlying_folder(db_session):
    owner = uuid.uuid4()
    reader = uuid.uuid4()
    stranger = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        folder_id = (await client.post("/api/v1/folders", json={"name": "Clients"})).json()["id"]
        share_id = (
            await client.post(
                f"/api/v1/folders/{folder_id}/shares",
                json={
                    "resource_type": "folder",
                    "resource_id": folder_id,
                    "principal_type": "user",
                    "principal_id": str(reader),
                    "level": "reader",
                },
            )
        ).json()["id"]

    async with _client_as(db_session, stranger) as client:
        response = await client.delete(f"/api/v1/shares/{share_id}")

    assert response.status_code == 403


async def test_remove_unknown_share_is_404(db_session):
    owner = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        response = await client.delete(f"/api/v1/shares/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_list_shares_requires_editor_access(db_session):
    owner = uuid.uuid4()
    reader = uuid.uuid4()
    async with _client_as(db_session, owner) as client:
        folder_id = (await client.post("/api/v1/folders", json={"name": "Clients"})).json()["id"]

    from app.db.models.enums import PermissionLevel as PL
    from app.db.models.enums import PrincipalType as PT
    from app.db.models.enums import ResourceType as RT
    from app.db.models.sharing import Share

    db_session.add(
        Share(
            resource_type=RT.folder,
            resource_id=uuid.UUID(folder_id),
            principal_type=PT.user,
            principal_id=reader,
            level=PL.reader,
            created_by=owner,
        )
    )
    await db_session.commit()

    async with _client_as(db_session, reader) as client:
        response = await client.get(f"/api/v1/folders/{folder_id}/shares")

    assert response.status_code == 403
