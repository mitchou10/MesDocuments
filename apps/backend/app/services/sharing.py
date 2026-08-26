import uuid

from app.db.models.enums import PermissionLevel, PrincipalType, ResourceType
from app.db.models.sharing import Share
from app.repositories.shares import ShareRepository


class ShareNotFoundError(Exception):
    def __init__(self, share_id: uuid.UUID) -> None:
        self.share_id = share_id
        super().__init__(f"Share {share_id} not found")


class ShareService:
    def __init__(self, repository: ShareRepository) -> None:
        self._repository = repository

    async def list_shares(self, resource_type: ResourceType, resource_id: uuid.UUID) -> list[Share]:
        return await self._repository.list_for_resource(resource_type, resource_id)

    async def add_share(
        self,
        *,
        resource_type: ResourceType,
        resource_id: uuid.UUID,
        principal_type: PrincipalType,
        principal_id: uuid.UUID,
        level: PermissionLevel,
        created_by: uuid.UUID,
    ) -> Share:
        # Sharing again with the same principal updates their level instead
        # of creating a duplicate grant - matches the "Partager" modal's UX,
        # where changing someone's role is just picking a different option.
        existing = await self._repository.find(
            resource_type=resource_type,
            resource_id=resource_id,
            principal_type=principal_type,
            principal_id=principal_id,
        )
        if existing is not None:
            return await self._repository.update_level(existing, level)

        return await self._repository.create(
            resource_type=resource_type,
            resource_id=resource_id,
            principal_type=principal_type,
            principal_id=principal_id,
            level=level,
            created_by=created_by,
        )

    async def get_share(self, share_id: uuid.UUID) -> Share:
        share = await self._repository.get(share_id)
        if share is None:
            raise ShareNotFoundError(share_id)
        return share

    async def remove_share(self, share_id: uuid.UUID) -> None:
        share = await self.get_share(share_id)
        await self._repository.delete(share)
