import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.users import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, user_id: uuid.UUID) -> User | None:
        return await self._session.get(User, user_id)

    async def search(self, query: str, *, limit: int = 10) -> list[User]:
        """Matches on username, display name or email - whichever the sharer
        happens to remember about the person they're looking for."""
        pattern = f"%{query}%"
        stmt = (
            select(User)
            .where(
                or_(
                    User.username.ilike(pattern),
                    User.display_name.ilike(pattern),
                    User.email.ilike(pattern),
                )
            )
            .order_by(User.username)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def upsert(
        self,
        *,
        id: uuid.UUID,
        username: str | None,
        email: str | None,
        display_name: str | None,
    ) -> User:
        """Keeps the local shadow row in sync with Keycloak's claims.

        Called on every request needing a local FK target - Keycloak is the
        identity source of truth, so this never creates a user on its own,
        only mirrors one that just proved it's authenticated.
        """
        user = await self.get(id)
        if user is None:
            user = User(id=id, username=username, email=email, display_name=display_name)
            self._session.add(user)
        else:
            user.username = username
            user.email = email
            user.display_name = display_name
        await self._session.flush()
        return user
