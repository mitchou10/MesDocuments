import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import PermissionLevel, PrincipalType, ResourceType
from app.db.models.sharing import Share


class ShareRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, share_id: uuid.UUID) -> Share | None:
        return await self._session.get(Share, share_id)

    async def list_for_resource(self, resource_type: ResourceType, resource_id: uuid.UUID) -> list[Share]:
        stmt = select(Share).where(Share.resource_type == resource_type, Share.resource_id == resource_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find(
        self,
        *,
        resource_type: ResourceType,
        resource_id: uuid.UUID,
        principal_type: PrincipalType,
        principal_id: uuid.UUID,
    ) -> Share | None:
        stmt = select(Share).where(
            Share.resource_type == resource_type,
            Share.resource_id == resource_id,
            Share.principal_type == principal_type,
            Share.principal_id == principal_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        resource_type: ResourceType,
        resource_id: uuid.UUID,
        principal_type: PrincipalType,
        principal_id: uuid.UUID,
        level: PermissionLevel,
        created_by: uuid.UUID,
    ) -> Share:
        share = Share(
            resource_type=resource_type,
            resource_id=resource_id,
            principal_type=principal_type,
            principal_id=principal_id,
            level=level,
            created_by=created_by,
        )
        self._session.add(share)
        await self._session.flush()
        return share

    async def update_level(self, share: Share, level: PermissionLevel) -> Share:
        share.level = level
        await self._session.flush()
        return share

    async def delete(self, share: Share) -> None:
        await self._session.delete(share)
        await self._session.flush()
