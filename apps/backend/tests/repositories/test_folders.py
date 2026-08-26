import uuid
from datetime import UTC, datetime

from app.repositories.folders import FolderRepository
from app.schemas.pagination import PageParams


async def test_create_and_get(db_session, make_user):
    owner = await make_user()
    repo = FolderRepository(db_session)

    folder = await repo.create(name="Clients", parent_id=None, owner_id=owner.id)

    fetched = await repo.get(folder.id)
    assert fetched is not None
    assert fetched.name == "Clients"
    assert fetched.parent_id is None
    assert fetched.owner_id == owner.id


async def test_get_returns_none_for_unknown_id(db_session):
    repo = FolderRepository(db_session)

    assert await repo.get(uuid.uuid4()) is None


async def test_get_children_orders_by_name_and_excludes_deleted(db_session, make_user):
    owner = await make_user()
    repo = FolderRepository(db_session)
    parent = await repo.create(name="Clients", parent_id=None, owner_id=owner.id)
    zebra = await repo.create(name="Zebra", parent_id=parent.id, owner_id=owner.id)
    acme = await repo.create(name="ACME", parent_id=parent.id, owner_id=owner.id)
    deleted = await repo.create(name="Deleted", parent_id=parent.id, owner_id=owner.id)
    await repo.soft_delete(deleted, deleted_at=datetime.now(UTC))

    page = await repo.get_children(parent.id, PageParams())

    assert [f.name for f in page.items] == ["ACME", "Zebra"]
    assert page.total == 2
    assert acme.id in {f.id for f in page.items}
    assert zebra.id in {f.id for f in page.items}


async def test_get_children_of_root_excludes_other_folders_children(db_session, make_user):
    owner = await make_user()
    repo = FolderRepository(db_session)
    parent = await repo.create(name="Clients", parent_id=None, owner_id=owner.id)
    await repo.create(name="ACME", parent_id=parent.id, owner_id=owner.id)

    page = await repo.get_children(None, PageParams())

    assert [f.name for f in page.items] == ["Clients"]
    assert page.total == 1


async def test_get_children_paginates(db_session, make_user):
    owner = await make_user()
    repo = FolderRepository(db_session)
    parent = await repo.create(name="Clients", parent_id=None, owner_id=owner.id)
    for name in ["Alpha", "Bravo", "Charlie", "Delta", "Echo"]:
        await repo.create(name=name, parent_id=parent.id, owner_id=owner.id)

    first_page = await repo.get_children(parent.id, PageParams(limit=2, offset=0))
    second_page = await repo.get_children(parent.id, PageParams(limit=2, offset=2))
    last_page = await repo.get_children(parent.id, PageParams(limit=2, offset=4))

    assert [f.name for f in first_page.items] == ["Alpha", "Bravo"]
    assert first_page.total == 5
    assert first_page.has_more is True

    assert [f.name for f in second_page.items] == ["Charlie", "Delta"]
    assert second_page.has_more is True

    assert [f.name for f in last_page.items] == ["Echo"]
    assert last_page.has_more is False


async def test_list_by_owner_returns_all_folders_regardless_of_depth(db_session, make_user):
    owner = await make_user()
    other_owner = await make_user(id=uuid.uuid4(), username="bob", email="bob@example.fr")
    repo = FolderRepository(db_session)
    clients = await repo.create(name="Clients", parent_id=None, owner_id=owner.id)
    await repo.create(name="ACME", parent_id=clients.id, owner_id=owner.id)
    await repo.create(name="Other", parent_id=None, owner_id=other_owner.id)

    page = await repo.list_by_owner(owner.id, PageParams())

    assert {f.name for f in page.items} == {"Clients", "ACME"}
    assert page.total == 2


async def test_rename(db_session, make_user):
    owner = await make_user()
    repo = FolderRepository(db_session)
    folder = await repo.create(name="Clients", parent_id=None, owner_id=owner.id)

    renamed = await repo.rename(folder, "Clients (archive)")

    assert renamed.name == "Clients (archive)"
    assert (await repo.get(folder.id)).name == "Clients (archive)"


async def test_soft_delete_sets_deleted_at(db_session, make_user):
    owner = await make_user()
    repo = FolderRepository(db_session)
    folder = await repo.create(name="Clients", parent_id=None, owner_id=owner.id)
    now = datetime.now(UTC)

    await repo.soft_delete(folder, deleted_at=now)

    fetched = await repo.get(folder.id)
    assert fetched.deleted_at is not None
