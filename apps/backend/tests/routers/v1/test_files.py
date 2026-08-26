import uuid

from app.db.models.enums import PermissionLevel, PrincipalType, ResourceType
from app.db.models.sharing import Share
from tests.routers.v1.conftest import client_as


async def _create_folder(db_session, owner: uuid.UUID, name: str = "Clients") -> str:
    async with client_as(db_session, owner) as client:
        response = await client.post("/api/v1/folders", json={"name": name})
    return response.json()["id"]


async def test_upload_and_get_file(db_session, storage_service):
    owner = uuid.uuid4()
    folder_id = await _create_folder(db_session, owner)

    async with client_as(db_session, owner) as client:
        upload = await client.post(
            f"/api/v1/folders/{folder_id}/files",
            files={"file": ("contrat.pdf", b"hello world", "application/pdf")},
        )
        assert upload.status_code == 201
        body = upload.json()
        assert body["name"] == "contrat.pdf"
        assert body["kind"] == "pdf"
        assert body["size_bytes"] == len(b"hello world")
        file_id = body["id"]

        get_response = await client.get(f"/api/v1/files/{file_id}")

    assert get_response.status_code == 200
    assert get_response.json()["id"] == file_id


async def test_upload_uses_explicit_name_over_filename(db_session, storage_service):
    owner = uuid.uuid4()
    folder_id = await _create_folder(db_session, owner)

    async with client_as(db_session, owner) as client:
        upload = await client.post(
            f"/api/v1/folders/{folder_id}/files",
            data={"name": "renamed.pdf"},
            files={"file": ("original.pdf", b"x", "application/pdf")},
        )

    assert upload.json()["name"] == "renamed.pdf"


async def test_list_files_in_folder(db_session, storage_service):
    owner = uuid.uuid4()
    folder_id = await _create_folder(db_session, owner)

    async with client_as(db_session, owner) as client:
        await client.post(
            f"/api/v1/folders/{folder_id}/files", files={"file": ("a.pdf", b"x", "application/pdf")}
        )
        await client.post(
            f"/api/v1/folders/{folder_id}/files", files={"file": ("b.pdf", b"y", "application/pdf")}
        )

        response = await client.get(f"/api/v1/folders/{folder_id}/files")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert {f["name"] for f in body["items"]} == {"a.pdf", "b.pdf"}


async def test_download_file_returns_original_bytes(db_session, storage_service):
    owner = uuid.uuid4()
    folder_id = await _create_folder(db_session, owner)
    content = b"le contenu exact du fichier"

    async with client_as(db_session, owner) as client:
        upload = await client.post(
            f"/api/v1/folders/{folder_id}/files",
            files={"file": ("doc.pdf", content, "application/pdf")},
        )
        file_id = upload.json()["id"]

        response = await client.get(f"/api/v1/files/{file_id}/download")

    assert response.status_code == 200
    assert response.content == content
    assert "doc.pdf" in response.headers["content-disposition"]


async def test_upload_requires_editor_access_on_folder(db_session, storage_service):
    owner = uuid.uuid4()
    reader = uuid.uuid4()
    folder_id = await _create_folder(db_session, owner)
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

    async with client_as(db_session, reader) as client:
        response = await client.post(
            f"/api/v1/folders/{folder_id}/files", files={"file": ("a.pdf", b"x", "application/pdf")}
        )

    assert response.status_code == 403


async def test_get_file_denies_access_to_non_owner_without_share(db_session, storage_service):
    owner = uuid.uuid4()
    stranger = uuid.uuid4()
    folder_id = await _create_folder(db_session, owner)

    async with client_as(db_session, owner) as client:
        upload = await client.post(
            f"/api/v1/folders/{folder_id}/files", files={"file": ("a.pdf", b"x", "application/pdf")}
        )
    file_id = upload.json()["id"]

    async with client_as(db_session, stranger) as client:
        response = await client.get(f"/api/v1/files/{file_id}")

    assert response.status_code == 403


async def test_get_file_not_found(db_session, storage_service):
    async with client_as(db_session, uuid.uuid4()) as client:
        response = await client.get(f"/api/v1/files/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_rename_file(db_session, storage_service):
    owner = uuid.uuid4()
    folder_id = await _create_folder(db_session, owner)

    async with client_as(db_session, owner) as client:
        upload = await client.post(
            f"/api/v1/folders/{folder_id}/files", files={"file": ("a.pdf", b"x", "application/pdf")}
        )
        file_id = upload.json()["id"]

        response = await client.patch(f"/api/v1/files/{file_id}", json={"name": "b.pdf"})

    assert response.status_code == 200
    assert response.json()["name"] == "b.pdf"


async def test_delete_file_then_download_is_not_found(db_session, storage_service):
    owner = uuid.uuid4()
    folder_id = await _create_folder(db_session, owner)

    async with client_as(db_session, owner) as client:
        upload = await client.post(
            f"/api/v1/folders/{folder_id}/files", files={"file": ("a.pdf", b"x", "application/pdf")}
        )
        file_id = upload.json()["id"]

        delete_response = await client.delete(f"/api/v1/files/{file_id}")
        get_response = await client.get(f"/api/v1/files/{file_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


async def test_deleting_a_folder_cascades_to_its_files(db_session, storage_service):
    owner = uuid.uuid4()
    folder_id = await _create_folder(db_session, owner)

    async with client_as(db_session, owner) as client:
        upload = await client.post(
            f"/api/v1/folders/{folder_id}/files", files={"file": ("a.pdf", b"x", "application/pdf")}
        )
        file_id = upload.json()["id"]

        delete_folder_response = await client.delete(f"/api/v1/folders/{folder_id}")
        get_file_response = await client.get(f"/api/v1/files/{file_id}")

    assert delete_folder_response.status_code == 204
    assert get_file_response.status_code == 404
