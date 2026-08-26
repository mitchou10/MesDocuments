import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.users import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, user_id: uuid.UUID) -> User | None:
        return await self._session.get(User, user_id)

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
