import uuid

from app.db.models.enums import PermissionLevel, PrincipalType, ResourceType
from app.repositories.folders import FolderRepository
from app.repositories.shares import ShareRepository


async def test_create_and_list_for_resource(db_session, make_user):
    owner = await make_user()
    reader = await make_user(id=uuid.uuid4(), username="bob", email="bob@example.fr")
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    repo = ShareRepository(db_session)

    share = await repo.create(
        resource_type=ResourceType.folder,
        resource_id=folder.id,
        principal_type=PrincipalType.user,
        principal_id=reader.id,
        level=PermissionLevel.reader,
        created_by=owner.id,
    )

    shares = await repo.list_for_resource(ResourceType.folder, folder.id)
    assert [s.id for s in shares] == [share.id]


async def test_list_for_resource_empty(db_session):
    shares = await ShareRepository(db_session).list_for_resource(ResourceType.folder, uuid.uuid4())
    assert shares == []


async def test_find_returns_existing_share(db_session, make_user):
    owner = await make_user()
    reader = await make_user(id=uuid.uuid4(), username="bob", email="bob@example.fr")
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    repo = ShareRepository(db_session)
    share = await repo.create(
        resource_type=ResourceType.folder,
        resource_id=folder.id,
        principal_type=PrincipalType.user,
        principal_id=reader.id,
        level=PermissionLevel.reader,
        created_by=owner.id,
    )

    found = await repo.find(
        resource_type=ResourceType.folder,
        resource_id=folder.id,
        principal_type=PrincipalType.user,
        principal_id=reader.id,
    )

    assert found is not None
    assert found.id == share.id


async def test_find_returns_none_when_no_match(db_session, make_user):
    owner = await make_user()
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    repo = ShareRepository(db_session)

    found = await repo.find(
        resource_type=ResourceType.folder,
        resource_id=folder.id,
        principal_type=PrincipalType.user,
        principal_id=uuid.uuid4(),
    )

    assert found is None


async def test_update_level(db_session, make_user):
    owner = await make_user()
    reader = await make_user(id=uuid.uuid4(), username="bob", email="bob@example.fr")
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    repo = ShareRepository(db_session)
    share = await repo.create(
        resource_type=ResourceType.folder,
        resource_id=folder.id,
        principal_type=PrincipalType.user,
        principal_id=reader.id,
        level=PermissionLevel.reader,
        created_by=owner.id,
    )

    updated = await repo.update_level(share, PermissionLevel.editor)

    assert updated.level == PermissionLevel.editor


async def test_delete(db_session, make_user):
    owner = await make_user()
    reader = await make_user(id=uuid.uuid4(), username="bob", email="bob@example.fr")
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    repo = ShareRepository(db_session)
    share = await repo.create(
        resource_type=ResourceType.folder,
        resource_id=folder.id,
        principal_type=PrincipalType.user,
        principal_id=reader.id,
        level=PermissionLevel.reader,
        created_by=owner.id,
    )

    await repo.delete(share)

    assert await repo.get(share.id) is None
