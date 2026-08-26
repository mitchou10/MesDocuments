import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import PermissionLevel, ResourceType
from app.db.models.users import User
from app.db.session import get_db
from app.dependencies.current_user import get_current_db_user
from app.dependencies.folders import get_folder_permission_service, get_folder_service
from app.dependencies.sharing import get_share_service
from app.routers.v1._folder_access import get_folder_or_404, require_folder_access
from app.schemas.sharing import ShareCreate, ShareRead
from app.services.folders import FolderService
from app.services.permissions import FolderPermissionService
from app.services.sharing import ShareNotFoundError, ShareService

router = APIRouter(tags=["sharing"])


@router.get("/folders/{folder_id}/shares")
async def list_folder_shares(
    folder_id: uuid.UUID,
    current_user: User = Depends(get_current_db_user),
    folder_service: FolderService = Depends(get_folder_service),
    permission_service: FolderPermissionService = Depends(get_folder_permission_service),
    share_service: ShareService = Depends(get_share_service),
) -> list[ShareRead]:
    folder = await get_folder_or_404(folder_service, folder_id)
    await require_folder_access(permission_service, current_user.id, folder, PermissionLevel.editor)

    shares = await share_service.list_shares(ResourceType.folder, folder_id)
    return [ShareRead.model_validate(share) for share in shares]


@router.post("/folders/{folder_id}/shares", status_code=status.HTTP_201_CREATED)
async def add_folder_share(
    folder_id: uuid.UUID,
    payload: ShareCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_db_user),
    folder_service: FolderService = Depends(get_folder_service),
    permission_service: FolderPermissionService = Depends(get_folder_permission_service),
    share_service: ShareService = Depends(get_share_service),
) -> ShareRead:
    folder = await get_folder_or_404(folder_service, folder_id)
    await require_folder_access(permission_service, current_user.id, folder, PermissionLevel.editor)

    if payload.resource_type != ResourceType.folder or payload.resource_id != folder_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="resource_type/resource_id must match the folder in the URL",
        )

    share = await share_service.add_share(
        resource_type=ResourceType.folder,
        resource_id=folder_id,
        principal_type=payload.principal_type,
        principal_id=payload.principal_id,
        level=payload.level,
        created_by=current_user.id,
    )
    await session.commit()
    return ShareRead.model_validate(share)


@router.delete("/shares/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_share(
    share_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_db_user),
    folder_service: FolderService = Depends(get_folder_service),
    permission_service: FolderPermissionService = Depends(get_folder_permission_service),
    share_service: ShareService = Depends(get_share_service),
) -> None:
    try:
        share = await share_service.get_share(share_id)
    except ShareNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found") from exc

    # Only folders exist as a real shareable resource today - this is the
    # one place that will need a branch once files can be shared directly.
    if share.resource_type == ResourceType.folder:
        folder = await get_folder_or_404(folder_service, share.resource_id)
        await require_folder_access(permission_service, current_user.id, folder, PermissionLevel.editor)

    await share_service.remove_share(share_id)
    await session.commit()
