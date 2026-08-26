from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.shares import ShareRepository
from app.services.sharing import ShareService


def get_share_service(session: AsyncSession = Depends(get_db)) -> ShareService:
    return ShareService(ShareRepository(session))
