import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.models.users import User
from app.dependencies.current_user import get_current_db_user
from app.dependencies.users import get_user_service
from app.schemas.users import UserRead
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/search")
async def search_users(
    q: str = Query(min_length=1),
    current_user: User = Depends(get_current_db_user),
    user_service: UserService = Depends(get_user_service),
) -> list[UserRead]:
    """Lets a sharer resolve "who am I sharing with" to a real user id -
    any authenticated user can search, same as picking a name out of a
    company directory."""
    users = await user_service.search_users(q)
    return [UserRead.model_validate(user) for user in users]


@router.get("/{user_id}")
async def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_db_user),
    user_service: UserService = Depends(get_user_service),
) -> UserRead:
    """The other half of sharing: a share only stores a principal_id, so
    rendering "who has access" needs this to turn ids back into names."""
    user = await user_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserRead.model_validate(user)
