from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.files import FileRepository
from app.services.files import FileService
from app.services.storage import StorageService, get_storage_service


def get_file_service(
    session: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(get_storage_service),
) -> FileService:
    return FileService(FileRepository(session), storage)
