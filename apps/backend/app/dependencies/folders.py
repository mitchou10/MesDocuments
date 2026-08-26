from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.folders import FolderRepository
from app.repositories.groups import GroupRepository
from app.repositories.shares import ShareRepository
from app.services.folders import FolderService
from app.services.permissions import FolderPermissionService


def get_folder_service(session: AsyncSession = Depends(get_db)) -> FolderService:
    return FolderService(FolderRepository(session))


def get_folder_permission_service(session: AsyncSession = Depends(get_db)) -> FolderPermissionService:
    return FolderPermissionService(
        FolderRepository(session), ShareRepository(session), GroupRepository(session)
    )
