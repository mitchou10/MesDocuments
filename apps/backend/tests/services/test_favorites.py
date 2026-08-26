from app.db.models.enums import ResourceType
from app.repositories.favorites import FavoriteRepository
from app.repositories.folders import FolderRepository
from app.schemas.pagination import PageParams
from app.services.favorites import FavoriteService


async def test_toggle_favorite_adds_then_removes(db_session, make_user):
    owner = await make_user()
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    service = FavoriteService(FavoriteRepository(db_session))

    first = await service.toggle_favorite(owner.id, ResourceType.folder, folder.id)
    second = await service.toggle_favorite(owner.id, ResourceType.folder, folder.id)

    assert first is True
    assert second is False


async def test_list_favorite_folders(db_session, make_user):
    owner = await make_user()
    folder = await FolderRepository(db_session).create(name="Clients", parent_id=None, owner_id=owner.id)
    service = FavoriteService(FavoriteRepository(db_session))
    await service.toggle_favorite(owner.id, ResourceType.folder, folder.id)

    page = await service.list_favorite_folders(owner.id, PageParams())

    assert [f.id for f in page.items] == [folder.id]


async def test_list_favorite_folders_empty_for_new_user(db_session, make_user):
    owner = await make_user()
    service = FavoriteService(FavoriteRepository(db_session))

    page = await service.list_favorite_folders(owner.id, PageParams())

    assert page.items == []
    assert page.total == 0
