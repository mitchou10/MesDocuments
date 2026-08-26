import uuid
from datetime import UTC, datetime

from app.db.models.enums import FileKind
from app.repositories.files import FileRepository
from app.repositories.folders import FolderRepository
from app.schemas.pagination import PageParams


async def _make_folder(db_session, owner_id):
    return await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner_id)


async def test_create_and_get(db_session, make_user):
    owner = await make_user()
    folder = await _make_folder(db_session, owner.id)
    repo = FileRepository(db_session)

    file = await repo.create(
        id=uuid.uuid4(),
        name="contrat.pdf",
        kind=FileKind.pdf,
        mime_type="application/pdf",
        size_bytes=1234,
        folder_id=folder.id,
        owner_id=owner.id,
    )

    fetched = await repo.get(file.id)
    assert fetched is not None
    assert fetched.name == "contrat.pdf"
    assert fetched.kind == FileKind.pdf
    assert fetched.folder_id == folder.id


async def test_get_returns_none_for_unknown_id(db_session):
    assert await FileRepository(db_session).get(uuid.uuid4()) is None


async def test_get_children_orders_and_excludes_deleted(db_session, make_user):
    owner = await make_user()
    folder = await _make_folder(db_session, owner.id)
    repo = FileRepository(db_session)
    zebra = await repo.create(
        id=uuid.uuid4(),
        name="zebra.pdf",
        kind=FileKind.pdf,
        mime_type="application/pdf",
        size_bytes=1,
        folder_id=folder.id,
        owner_id=owner.id,
    )
    acme = await repo.create(
        id=uuid.uuid4(),
        name="acme.pdf",
        kind=FileKind.pdf,
        mime_type="application/pdf",
        size_bytes=1,
        folder_id=folder.id,
        owner_id=owner.id,
    )
    deleted = await repo.create(
        id=uuid.uuid4(),
        name="deleted.pdf",
        kind=FileKind.pdf,
        mime_type="application/pdf",
        size_bytes=1,
        folder_id=folder.id,
        owner_id=owner.id,
    )
    await repo.soft_delete(deleted, deleted_at=datetime.now(UTC))

    page = await repo.get_children(folder.id, PageParams())

    assert [f.name for f in page.items] == ["acme.pdf", "zebra.pdf"]
    assert page.total == 2
    assert acme.id in {f.id for f in page.items}
    assert zebra.id in {f.id for f in page.items}


async def test_create_version_and_get_latest(db_session, make_user):
    owner = await make_user()
    folder = await _make_folder(db_session, owner.id)
    repo = FileRepository(db_session)
    file = await repo.create(
        id=uuid.uuid4(),
        name="a.pdf",
        kind=FileKind.pdf,
        mime_type="application/pdf",
        size_bytes=1,
        folder_id=folder.id,
        owner_id=owner.id,
    )

    await repo.create_version(
        file_id=file.id,
        version_number=1,
        storage_key="k1",
        content_hash="h1",
        size_bytes=1,
        author_id=owner.id,
    )
    v2 = await repo.create_version(
        file_id=file.id,
        version_number=2,
        storage_key="k2",
        content_hash="h2",
        size_bytes=2,
        author_id=owner.id,
    )

    latest = await repo.get_latest_version(file.id)
    assert latest is not None
    assert latest.id == v2.id

    versions = await repo.get_versions(file.id)
    assert [v.version_number for v in versions] == [2, 1]


async def test_get_latest_version_none_when_no_versions(db_session, make_user):
    owner = await make_user()
    folder = await _make_folder(db_session, owner.id)
    repo = FileRepository(db_session)
    file = await repo.create(
        id=uuid.uuid4(),
        name="a.pdf",
        kind=FileKind.pdf,
        mime_type="application/pdf",
        size_bytes=1,
        folder_id=folder.id,
        owner_id=owner.id,
    )

    assert await repo.get_latest_version(file.id) is None


async def test_rename(db_session, make_user):
    owner = await make_user()
    folder = await _make_folder(db_session, owner.id)
    repo = FileRepository(db_session)
    file = await repo.create(
        id=uuid.uuid4(),
        name="a.pdf",
        kind=FileKind.pdf,
        mime_type="application/pdf",
        size_bytes=1,
        folder_id=folder.id,
        owner_id=owner.id,
    )

    renamed = await repo.rename(file, "b.pdf")

    assert renamed.name == "b.pdf"
    assert (await repo.get(file.id)).name == "b.pdf"


async def test_soft_delete_sets_deleted_at(db_session, make_user):
    owner = await make_user()
    folder = await _make_folder(db_session, owner.id)
    repo = FileRepository(db_session)
    file = await repo.create(
        id=uuid.uuid4(),
        name="a.pdf",
        kind=FileKind.pdf,
        mime_type="application/pdf",
        size_bytes=1,
        folder_id=folder.id,
        owner_id=owner.id,
    )

    await repo.soft_delete(file, deleted_at=datetime.now(UTC))

    assert (await repo.get(file.id)).deleted_at is not None
