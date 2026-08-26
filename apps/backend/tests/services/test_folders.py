import uuid

import pytest

from app.repositories.folders import FolderRepository
from app.schemas.pagination import PageParams
from app.services.folders import FolderNotFoundError, FolderService, InvalidFolderNameError


async def test_create_folder_trims_whitespace(db_session, make_user):
    owner = await make_user()
    service = FolderService(FolderRepository(db_session))

    folder = await service.create_folder(name="  Clients  ", parent_id=None, owner_id=owner.id)

    assert folder.name == "Clients"


async def test_create_folder_rejects_empty_name(db_session, make_user):
    owner = await make_user()
    service = FolderService(FolderRepository(db_session))

    with pytest.raises(InvalidFolderNameError):
        await service.create_folder(name="   ", parent_id=None, owner_id=owner.id)


async def test_create_folder_requires_existing_parent(db_session, make_user):
    owner = await make_user()
    service = FolderService(FolderRepository(db_session))

    with pytest.raises(FolderNotFoundError):
        await service.create_folder(name="ACME", parent_id=uuid.uuid4(), owner_id=owner.id)


async def test_get_folder_raises_for_deleted_folder(db_session, make_user):
    owner = await make_user()
    service = FolderService(FolderRepository(db_session))
    folder = await service.create_folder(name="Clients", parent_id=None, owner_id=owner.id)
    await service.delete_folder(folder.id)

    with pytest.raises(FolderNotFoundError):
        await service.get_folder(folder.id)


async def test_rename_folder_rejects_empty_name(db_session, make_user):
    owner = await make_user()
    service = FolderService(FolderRepository(db_session))
    folder = await service.create_folder(name="Clients", parent_id=None, owner_id=owner.id)

    with pytest.raises(InvalidFolderNameError):
        await service.rename_folder(folder.id, "   ")


async def test_get_path_builds_breadcrumb_root_to_parent(db_session, make_user):
    owner = await make_user()
    service = FolderService(FolderRepository(db_session))
    clients = await service.create_folder(name="Clients", parent_id=None, owner_id=owner.id)
    acme = await service.create_folder(name="ACME", parent_id=clients.id, owner_id=owner.id)
    contracts = await service.create_folder(name="Contrats", parent_id=acme.id, owner_id=owner.id)

    path = await service.get_path(contracts.id)

    assert [f.name for f in path] == ["Clients", "ACME"]


async def test_get_path_of_root_folder_is_empty(db_session, make_user):
    owner = await make_user()
    service = FolderService(FolderRepository(db_session))
    root = await service.create_folder(name="Clients", parent_id=None, owner_id=owner.id)

    assert await service.get_path(root.id) == []


async def test_get_children_of_root_when_none_requested(db_session, make_user):
    owner = await make_user()
    service = FolderService(FolderRepository(db_session))
    await service.create_folder(name="Clients", parent_id=None, owner_id=owner.id)

    tree = await service.get_children(None, PageParams())

    assert tree.folder is None
    assert [f.name for f in tree.subfolders.items] == ["Clients"]
    assert tree.subfolders.total == 1


async def test_get_children_paginates_through_service(db_session, make_user):
    owner = await make_user()
    service = FolderService(FolderRepository(db_session))
    parent = await service.create_folder(name="Clients", parent_id=None, owner_id=owner.id)
    for name in ["Alpha", "Bravo", "Charlie"]:
        await service.create_folder(name=name, parent_id=parent.id, owner_id=owner.id)

    tree = await service.get_children(parent.id, PageParams(limit=2, offset=0))

    assert tree.folder is not None and tree.folder.id == parent.id
    assert [f.name for f in tree.subfolders.items] == ["Alpha", "Bravo"]
    assert tree.subfolders.total == 3
    assert tree.subfolders.has_more is True


async def test_list_folders_for_user(db_session, make_user):
    owner = await make_user()
    other_owner = await make_user(id=uuid.uuid4(), username="bob", email="bob@example.fr")
    service = FolderService(FolderRepository(db_session))
    clients = await service.create_folder(name="Clients", parent_id=None, owner_id=owner.id)
    await service.create_folder(name="ACME", parent_id=clients.id, owner_id=owner.id)
    await service.create_folder(name="Other", parent_id=None, owner_id=other_owner.id)

    page = await service.list_folders_for_user(owner.id, PageParams())

    assert {f.name for f in page.items} == {"Clients", "ACME"}
    assert page.total == 2
