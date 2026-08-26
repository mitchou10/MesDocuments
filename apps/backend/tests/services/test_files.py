import pytest

from app.db.models.enums import FileKind
from app.repositories.files import FileRepository
from app.repositories.folders import FolderRepository
from app.services.files import (
    FileNotFoundError,
    FileService,
    InvalidFileNameError,
    infer_kind,
)


async def _stream(*chunks: bytes):
    for chunk in chunks:
        yield chunk


@pytest.mark.parametrize(
    ("mime_type", "expected"),
    [
        ("application/pdf", FileKind.pdf),
        ("audio/mpeg", FileKind.audio),
        ("video/mp4", FileKind.video),
        ("image/png", FileKind.image),
        ("application/zip", FileKind.other),
        ("", FileKind.other),
    ],
)
def test_infer_kind(mime_type, expected):
    assert infer_kind(mime_type) == expected


async def test_upload_file_stores_bytes_and_metadata(db_session, make_user, storage_service):
    owner = await make_user()
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    service = FileService(FileRepository(db_session), storage_service)

    file = await service.upload_file(
        folder_id=folder.id,
        owner_id=owner.id,
        filename="contrat.pdf",
        content_type="application/pdf",
        stream=_stream(b"hello ", b"world"),
    )

    assert file.name == "contrat.pdf"
    assert file.kind == FileKind.pdf
    assert file.size_bytes == len(b"hello world")

    fetched, chunks = await service.download_file(file.id)
    assert fetched.id == file.id
    downloaded = b"".join([chunk async for chunk in chunks])
    assert downloaded == b"hello world"


async def test_upload_file_rejects_empty_name(db_session, make_user, storage_service):
    owner = await make_user()
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    service = FileService(FileRepository(db_session), storage_service)

    with pytest.raises(InvalidFileNameError):
        await service.upload_file(
            folder_id=folder.id,
            owner_id=owner.id,
            filename="   ",
            content_type="application/pdf",
            stream=_stream(b"x"),
        )


async def test_rename_file(db_session, make_user, storage_service):
    owner = await make_user()
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    service = FileService(FileRepository(db_session), storage_service)
    file = await service.upload_file(
        folder_id=folder.id,
        owner_id=owner.id,
        filename="a.pdf",
        content_type="application/pdf",
        stream=_stream(b"x"),
    )

    renamed = await service.rename_file(file.id, "b.pdf")

    assert renamed.name == "b.pdf"


async def test_delete_file_removes_storage_object(db_session, make_user, storage_service):
    owner = await make_user()
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    service = FileService(FileRepository(db_session), storage_service)
    file = await service.upload_file(
        folder_id=folder.id,
        owner_id=owner.id,
        filename="a.pdf",
        content_type="application/pdf",
        stream=_stream(b"x"),
    )
    version = await FileRepository(db_session).get_latest_version(file.id)

    await service.delete_file(file.id)

    with pytest.raises(FileNotFoundError):
        await service.get_file(file.id)

    # The object itself must be gone from storage too, not just the DB row.
    with pytest.raises(Exception):  # noqa: B017 - boto3 raises a dynamic ClientError subtype
        b"".join([chunk async for chunk in storage_service.download_stream(version.storage_key)])


async def test_delete_files_in_folders_cascades(db_session, make_user, storage_service):
    owner = await make_user()
    folder_repo = FolderRepository(db_session)
    folder = await folder_repo.create(name="Clients", parent_id=None, owner_id=owner.id)
    service = FileService(FileRepository(db_session), storage_service)
    file_a = await service.upload_file(
        folder_id=folder.id,
        owner_id=owner.id,
        filename="a.pdf",
        content_type="application/pdf",
        stream=_stream(b"x"),
    )
    file_b = await service.upload_file(
        folder_id=folder.id,
        owner_id=owner.id,
        filename="b.pdf",
        content_type="application/pdf",
        stream=_stream(b"y"),
    )

    await service.delete_files_in_folders([folder.id])

    with pytest.raises(FileNotFoundError):
        await service.get_file(file_a.id)
    with pytest.raises(FileNotFoundError):
        await service.get_file(file_b.id)
