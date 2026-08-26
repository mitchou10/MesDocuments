import uuid

from app.db.models.enums import ResourceType
from app.db.models.folders import Folder
from app.repositories.favorites import FavoriteRepository
from app.repositories.pagination import Page
from app.schemas.pagination import PageParams


class FavoriteService:
    def __init__(self, repository: FavoriteRepository) -> None:
        self._repository = repository

    async def toggle_favorite(
        self, user_id: uuid.UUID, resource_type: ResourceType, resource_id: uuid.UUID
    ) -> bool:
        """Adds the favorite if it doesn't exist, removes it otherwise.

        Returns the resulting state (True = now favorited) so the router can
        report it without a second read.
        """
        existing = await self._repository.get(user_id, resource_type, resource_id)
        if existing is not None:
            await self._repository.remove(existing)
            return False

        await self._repository.add(user_id, resource_type, resource_id)
        return True

    async def list_favorite_folders(self, user_id: uuid.UUID, page: PageParams) -> Page[Folder]:
        return await self._repository.list_favorite_folders(user_id, page)
