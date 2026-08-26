import uuid

from app.db.models.enums import ResourceType
from app.repositories.favorites import FavoriteRepository
from app.repositories.folders import FolderRepository
from app.schemas.pagination import PageParams


async def test_add_and_get(db_session, make_user):
    owner = await make_user()
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    repo = FavoriteRepository(db_session)

    favorite = await repo.add(owner.id, ResourceType.folder, folder.id)

    assert favorite.user_id == owner.id
    found = await repo.get(owner.id, ResourceType.folder, folder.id)
    assert found is not None
    assert found.resource_id == folder.id


async def test_get_returns_none_when_missing(db_session, make_user):
    owner = await make_user()
    repo = FavoriteRepository(db_session)

    found = await repo.get(owner.id, ResourceType.folder, uuid.uuid4())

    assert found is None


async def test_remove(db_session, make_user):
    owner = await make_user()
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    repo = FavoriteRepository(db_session)
    favorite = await repo.add(owner.id, ResourceType.folder, folder.id)

    await repo.remove(favorite)

    assert await repo.get(owner.id, ResourceType.folder, folder.id) is None


async def test_list_favorite_folders_only_returns_this_users_favorites(db_session, make_user):
    owner = await make_user()
    other = await make_user(id=uuid.uuid4(), username="bob", email="bob@example.fr")
    folder_repo = FolderRepository(db_session)
    mine = await folder_repo.create(name="Mine", parent_id=None, owner_id=owner.id)
    theirs = await folder_repo.create(name="Theirs", parent_id=None, owner_id=other.id)
    repo = FavoriteRepository(db_session)
    await repo.add(owner.id, ResourceType.folder, mine.id)
    await repo.add(other.id, ResourceType.folder, theirs.id)

    page = await repo.list_favorite_folders(owner.id, PageParams())

    assert [f.id for f in page.items] == [mine.id]
    assert page.total == 1


async def test_list_favorite_folders_excludes_soft_deleted(db_session, make_user):
    owner = await make_user()
    folder_repo = FolderRepository(db_session)
    folder = await folder_repo.create(name="Clients", parent_id=None, owner_id=owner.id)
    repo = FavoriteRepository(db_session)
    await repo.add(owner.id, ResourceType.folder, folder.id)

    from datetime import UTC, datetime

    await folder_repo.soft_delete(folder, deleted_at=datetime.now(UTC))

    page = await repo.list_favorite_folders(owner.id, PageParams())

    assert page.items == []
    assert page.total == 0
