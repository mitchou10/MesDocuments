from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.favorites import FavoriteRepository
from app.services.favorites import FavoriteService


def get_favorite_service(session: AsyncSession = Depends(get_db)) -> FavoriteService:
    return FavoriteService(FavoriteRepository(session))
