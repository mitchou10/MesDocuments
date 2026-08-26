import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import PermissionLevel, ResourceType
from app.db.models.users import User
from app.db.session import get_db
from app.dependencies.current_user import get_current_db_user
from app.dependencies.favorites import get_favorite_service
from app.dependencies.folders import get_folder_permission_service, get_folder_service
from app.routers.v1._folder_access import get_folder_or_404, require_folder_access
from app.schemas.folders import FolderRead
from app.schemas.pagination import PageOut, PageParams
from app.schemas.sharing import FavoriteToggleResult
from app.services.favorites import FavoriteService
from app.services.folders import FolderService
from app.services.permissions import FolderPermissionService

router = APIRouter(tags=["favorites"])


@router.post("/folders/{folder_id}/favorite")
async def toggle_folder_favorite(
    folder_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_db_user),
    folder_service: FolderService = Depends(get_folder_service),
    permission_service: FolderPermissionService = Depends(get_folder_permission_service),
    favorite_service: FavoriteService = Depends(get_favorite_service),
) -> FavoriteToggleResult:
    folder = await get_folder_or_404(folder_service, folder_id)
    await require_folder_access(permission_service, current_user.id, folder, PermissionLevel.reader)

    favorited = await favorite_service.toggle_favorite(current_user.id, ResourceType.folder, folder_id)
    await session.commit()
    return FavoriteToggleResult(favorited=favorited)


@router.get("/favorites/folders")
async def list_favorite_folders(
    page: PageParams = Depends(),
    current_user: User = Depends(get_current_db_user),
    favorite_service: FavoriteService = Depends(get_favorite_service),
) -> PageOut[FolderRead]:
    result = await favorite_service.list_favorite_folders(current_user.id, page)
    return PageOut.from_page(result, FolderRead)
