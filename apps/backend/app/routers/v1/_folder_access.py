import uuid

from fastapi import HTTPException, status

from app.db.models.enums import PermissionLevel
from app.db.models.folders import Folder
from app.services.folders import FolderNotFoundError, FolderService
from app.services.permissions import AccessDeniedError, FolderPermissionService

# Shared by every router that needs "does this folder exist, and can this
# user access it" (folders, files, sharing) - kept in one place so the same
# 404 vs 403 behavior can't drift between them.


async def get_folder_or_404(folder_service: FolderService, folder_id: uuid.UUID) -> Folder:
    try:
        return await folder_service.get_folder(folder_id)
    except FolderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found") from exc


async def require_folder_access(
    permission_service: FolderPermissionService,
    user_id: uuid.UUID,
    folder: Folder,
    minimum: PermissionLevel = PermissionLevel.reader,
) -> None:
    try:
        await permission_service.require_access(user_id, folder, minimum)
    except AccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied") from exc
