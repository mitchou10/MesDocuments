import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import ResourceType
from app.db.models.sharing import Share


class ShareRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_resource(self, resource_type: ResourceType, resource_id: uuid.UUID) -> list[Share]:
        stmt = select(Share).where(Share.resource_type == resource_type, Share.resource_id == resource_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
