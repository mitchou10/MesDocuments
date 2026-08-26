import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.users import User
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.repositories.users import UserRepository
from app.schemas.auth import CurrentUser


async def get_current_db_user(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> User:
    """Keycloak authenticates; this makes sure a matching local row exists so
    other tables (folders.owner_id, etc.) have something to point a FK at."""
    repository = UserRepository(session)
    user = await repository.upsert(
        id=uuid.UUID(current_user.sub),
        username=current_user.username,
        email=current_user.email,
        display_name=current_user.name,
    )
    await session.commit()
    return user
