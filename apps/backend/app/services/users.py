import uuid

from app.db.models.users import User
from app.repositories.users import UserRepository

# A search shorter than this matches too broadly to be a useful "who am I
# sharing with" lookup, and turns every keystroke into a wide ILIKE scan.
MIN_QUERY_LENGTH = 2


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def search_users(self, query: str, *, limit: int = 10) -> list[User]:
        query = query.strip()
        if len(query) < MIN_QUERY_LENGTH:
            return []
        return await self._repository.search(query, limit=limit)

    async def get_user(self, user_id: uuid.UUID) -> User | None:
        return await self._repository.get(user_id)
