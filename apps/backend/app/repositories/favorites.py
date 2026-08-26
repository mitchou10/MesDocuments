import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import ResourceType
from app.db.models.folders import Folder
from app.db.models.sharing import Favorite
from app.repositories.pagination import Page
from app.schemas.pagination import PageParams


class FavoriteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(
        self, user_id: uuid.UUID, resource_type: ResourceType, resource_id: uuid.UUID
    ) -> Favorite | None:
        return await self._session.get(Favorite, (user_id, resource_type, resource_id))

    async def add(self, user_id: uuid.UUID, resource_type: ResourceType, resource_id: uuid.UUID) -> Favorite:
        favorite = Favorite(user_id=user_id, resource_type=resource_type, resource_id=resource_id)
        self._session.add(favorite)
        await self._session.flush()
        return favorite

    async def remove(self, favorite: Favorite) -> None:
        await self._session.delete(favorite)
        await self._session.flush()

    async def list_favorite_folders(self, user_id: uuid.UUID, page: PageParams) -> Page[Folder]:
        # Only folders can be favorited today, so this joins straight to
        # `folders` rather than returning a generic resource_id the caller
        # would then have to resolve themselves.
        condition = (
            (Favorite.user_id == user_id)
            & (Favorite.resource_type == ResourceType.folder)
            & (Folder.deleted_at.is_(None))
        )

        count_stmt = (
            select(func.count())
            .select_from(Favorite)
            .join(Folder, Favorite.resource_id == Folder.id)
            .where(condition)
        )
        total = (await self._session.execute(count_stmt)).scalar_one()

        items_stmt = (
            select(Folder)
            .join(Favorite, Favorite.resource_id == Folder.id)
            .where(condition)
            .order_by(Folder.name, Folder.id)
            .limit(page.limit)
            .offset(page.offset)
        )
        result = await self._session.execute(items_stmt)
        items = list(result.scalars().all())

        return Page(items=items, total=total, limit=page.limit, offset=page.offset)
