import uuid

import pytest

from app.db.models.enums import PermissionLevel, PrincipalType, ResourceType
from app.db.models.groups import Group, GroupMember
from app.db.models.sharing import Share
from app.repositories.folders import FolderRepository
from app.repositories.groups import GroupRepository
from app.repositories.shares import ShareRepository
from app.services.permissions import AccessDeniedError, FolderPermissionService


def _make_service(db_session) -> FolderPermissionService:
    return FolderPermissionService(
        FolderRepository(db_session), ShareRepository(db_session), GroupRepository(db_session)
    )


async def test_owner_always_has_editor_access(db_session, make_user):
    owner = await make_user()
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    service = _make_service(db_session)

    level = await service.get_access_level(owner.id, folder)

    assert level == PermissionLevel.editor


async def test_stranger_has_no_access(db_session, make_user):
    owner = await make_user()
    stranger = await make_user(id=uuid.uuid4(), username="bob", email="bob@example.fr")
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    service = _make_service(db_session)

    assert await service.get_access_level(stranger.id, folder) is None


async def test_direct_share_grants_access(db_session, make_user):
    owner = await make_user()
    reader = await make_user(id=uuid.uuid4(), username="bob", email="bob@example.fr")
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    db_session.add(
        Share(
            resource_type=ResourceType.folder,
            resource_id=folder.id,
            principal_type=PrincipalType.user,
            principal_id=reader.id,
            level=PermissionLevel.reader,
            created_by=owner.id,
        )
    )
    await db_session.flush()
    service = _make_service(db_session)

    assert await service.get_access_level(reader.id, folder) == PermissionLevel.reader


async def test_share_on_ancestor_is_inherited(db_session, make_user):
    owner = await make_user()
    reader = await make_user(id=uuid.uuid4(), username="bob", email="bob@example.fr")
    repo = FolderRepository(db_session)
    parent = await repo.create(name="Clients", parent_id=None, owner_id=owner.id)
    child = await repo.create(name="ACME", parent_id=parent.id, owner_id=owner.id)
    grandchild = await repo.create(name="Contrats", parent_id=child.id, owner_id=owner.id)
    db_session.add(
        Share(
            resource_type=ResourceType.folder,
            resource_id=parent.id,
            principal_type=PrincipalType.user,
            principal_id=reader.id,
            level=PermissionLevel.reader,
            created_by=owner.id,
        )
    )
    await db_session.flush()
    service = _make_service(db_session)

    assert await service.get_access_level(reader.id, grandchild) == PermissionLevel.reader


async def test_direct_share_overrides_a_weaker_inherited_one(db_session, make_user):
    owner = await make_user()
    editor = await make_user(id=uuid.uuid4(), username="bob", email="bob@example.fr")
    repo = FolderRepository(db_session)
    parent = await repo.create(name="Clients", parent_id=None, owner_id=owner.id)
    child = await repo.create(name="ACME", parent_id=parent.id, owner_id=owner.id)
    db_session.add_all(
        [
            Share(
                resource_type=ResourceType.folder,
                resource_id=parent.id,
                principal_type=PrincipalType.user,
                principal_id=editor.id,
                level=PermissionLevel.reader,
                created_by=owner.id,
            ),
            Share(
                resource_type=ResourceType.folder,
                resource_id=child.id,
                principal_type=PrincipalType.user,
                principal_id=editor.id,
                level=PermissionLevel.editor,
                created_by=owner.id,
            ),
        ]
    )
    await db_session.flush()
    service = _make_service(db_session)

    assert await service.get_access_level(editor.id, child) == PermissionLevel.editor


async def test_group_share_grants_access_to_its_members(db_session, make_user):
    owner = await make_user()
    member = await make_user(id=uuid.uuid4(), username="bob", email="bob@example.fr")
    group = Group(name="Finance", created_by=owner.id)
    db_session.add(group)
    await db_session.flush()
    db_session.add(GroupMember(group_id=group.id, user_id=member.id))
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    db_session.add(
        Share(
            resource_type=ResourceType.folder,
            resource_id=folder.id,
            principal_type=PrincipalType.group,
            principal_id=group.id,
            level=PermissionLevel.editor,
            created_by=owner.id,
        )
    )
    await db_session.flush()
    service = _make_service(db_session)

    assert await service.get_access_level(member.id, folder) == PermissionLevel.editor


async def test_require_access_raises_when_minimum_not_met(db_session, make_user):
    owner = await make_user()
    reader = await make_user(id=uuid.uuid4(), username="bob", email="bob@example.fr")
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    db_session.add(
        Share(
            resource_type=ResourceType.folder,
            resource_id=folder.id,
            principal_type=PrincipalType.user,
            principal_id=reader.id,
            level=PermissionLevel.reader,
            created_by=owner.id,
        )
    )
    await db_session.flush()
    service = _make_service(db_session)

    with pytest.raises(AccessDeniedError):
        await service.require_access(reader.id, folder, minimum=PermissionLevel.editor)
