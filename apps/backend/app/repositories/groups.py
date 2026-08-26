import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.groups import GroupMember


class GroupRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_group_ids_for_user(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        stmt = select(GroupMember.group_id).where(GroupMember.user_id == user_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
