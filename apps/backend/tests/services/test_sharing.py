import uuid

import pytest

from app.db.models.enums import PermissionLevel, PrincipalType, ResourceType
from app.repositories.folders import FolderRepository
from app.repositories.shares import ShareRepository
from app.services.sharing import ShareNotFoundError, ShareService


async def test_add_share_creates_new_grant(db_session, make_user):
    owner = await make_user()
    reader = await make_user(id=uuid.uuid4(), username="bob", email="bob@example.fr")
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    service = ShareService(ShareRepository(db_session))

    share = await service.add_share(
        resource_type=ResourceType.folder,
        resource_id=folder.id,
        principal_type=PrincipalType.user,
        principal_id=reader.id,
        level=PermissionLevel.reader,
        created_by=owner.id,
    )

    assert share.level == PermissionLevel.reader
    shares = await service.list_shares(ResourceType.folder, folder.id)
    assert [s.id for s in shares] == [share.id]


async def test_add_share_upserts_existing_grant_instead_of_duplicating(db_session, make_user):
    owner = await make_user()
    reader = await make_user(id=uuid.uuid4(), username="bob", email="bob@example.fr")
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    service = ShareService(ShareRepository(db_session))

    first = await service.add_share(
        resource_type=ResourceType.folder,
        resource_id=folder.id,
        principal_type=PrincipalType.user,
        principal_id=reader.id,
        level=PermissionLevel.reader,
        created_by=owner.id,
    )
    second = await service.add_share(
        resource_type=ResourceType.folder,
        resource_id=folder.id,
        principal_type=PrincipalType.user,
        principal_id=reader.id,
        level=PermissionLevel.editor,
        created_by=owner.id,
    )

    assert second.id == first.id
    assert second.level == PermissionLevel.editor
    shares = await service.list_shares(ResourceType.folder, folder.id)
    assert len(shares) == 1


async def test_get_share_raises_when_missing(db_session):
    service = ShareService(ShareRepository(db_session))

    with pytest.raises(ShareNotFoundError):
        await service.get_share(uuid.uuid4())


async def test_remove_share(db_session, make_user):
    owner = await make_user()
    reader = await make_user(id=uuid.uuid4(), username="bob", email="bob@example.fr")
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    service = ShareService(ShareRepository(db_session))
    share = await service.add_share(
        resource_type=ResourceType.folder,
        resource_id=folder.id,
        principal_type=PrincipalType.user,
        principal_id=reader.id,
        level=PermissionLevel.reader,
        created_by=owner.id,
    )

    await service.remove_share(share.id)

    with pytest.raises(ShareNotFoundError):
        await service.get_share(share.id)
