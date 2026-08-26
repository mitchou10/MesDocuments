import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import PermissionLevel
from app.db.models.users import User
from app.db.session import get_db
from app.dependencies.current_user import get_current_db_user
from app.dependencies.files import get_file_service
from app.dependencies.folders import get_folder_permission_service, get_folder_service
from app.routers.v1._folder_access import get_folder_or_404, require_folder_access
from app.schemas.folders import FolderCreate, FolderRead
from app.schemas.pagination import PageOut, PageParams
from app.services.files import FileService
from app.services.folders import FolderService, InvalidFolderNameError
from app.services.permissions import FolderPermissionService

router = APIRouter(prefix="/folders", tags=["folders"])


@router.get("")
async def list_root_folders(
    page: PageParams = Depends(),
    current_user: User = Depends(get_current_db_user),
    folder_service: FolderService = Depends(get_folder_service),
) -> PageOut[FolderRead]:
    """My top-level folders ("Mes documents"). Not the same as the children
    of some other folder - use GET /folders/{folder_id}/children for that."""
    result = await folder_service.list_root_folders_for_user(current_user.id, page)
    return PageOut.from_page(result, FolderRead)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_folder(
    payload: FolderCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_db_user),
    folder_service: FolderService = Depends(get_folder_service),
    permission_service: FolderPermissionService = Depends(get_folder_permission_service),
) -> FolderRead:
    if payload.parent_id is not None:
        parent = await get_folder_or_404(folder_service, payload.parent_id)
        await require_folder_access(permission_service, current_user.id, parent, PermissionLevel.editor)

    try:
        folder = await folder_service.create_folder(
            name=payload.name, parent_id=payload.parent_id, owner_id=current_user.id
        )
    except InvalidFolderNameError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    await session.commit()
    return FolderRead.model_validate(folder)


@router.get("/{folder_id}")
async def get_folder(
    folder_id: uuid.UUID,
    current_user: User = Depends(get_current_db_user),
    folder_service: FolderService = Depends(get_folder_service),
    permission_service: FolderPermissionService = Depends(get_folder_permission_service),
) -> FolderRead:
    folder = await get_folder_or_404(folder_service, folder_id)
    await require_folder_access(permission_service, current_user.id, folder, PermissionLevel.reader)
    return FolderRead.model_validate(folder)


@router.get("/{folder_id}/children")
async def list_children(
    folder_id: uuid.UUID,
    page: PageParams = Depends(),
    current_user: User = Depends(get_current_db_user),
    folder_service: FolderService = Depends(get_folder_service),
    permission_service: FolderPermissionService = Depends(get_folder_permission_service),
) -> PageOut[FolderRead]:
    folder = await get_folder_or_404(folder_service, folder_id)
    await require_folder_access(permission_service, current_user.id, folder, PermissionLevel.reader)

    tree = await folder_service.get_children(folder_id, page)
    return PageOut.from_page(tree.subfolders, FolderRead)


@router.patch("/{folder_id}")
async def rename_folder(
    folder_id: uuid.UUID,
    payload: FolderCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_db_user),
    folder_service: FolderService = Depends(get_folder_service),
    permission_service: FolderPermissionService = Depends(get_folder_permission_service),
) -> FolderRead:
    folder = await get_folder_or_404(folder_service, folder_id)
    await require_folder_access(permission_service, current_user.id, folder, PermissionLevel.editor)

    try:
        folder = await folder_service.rename_folder(folder_id, payload.name)
    except InvalidFolderNameError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    await session.commit()
    return FolderRead.model_validate(folder)


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_db_user),
    folder_service: FolderService = Depends(get_folder_service),
    file_service: FileService = Depends(get_file_service),
    permission_service: FolderPermissionService = Depends(get_folder_permission_service),
) -> None:
    folder = await get_folder_or_404(folder_service, folder_id)
    await require_folder_access(permission_service, current_user.id, folder, PermissionLevel.editor)

    # Cascade: the folder itself plus every descendant folder, then every
    # file inside any of them (which also purges their storage - see
    # FileService.delete_file). Nothing under a deleted folder stays visible
    # or keeps its bytes around.
    affected_folder_ids = await folder_service.delete_folder(folder_id)
    await file_service.delete_files_in_folders(affected_folder_ids)
    await session.commit()
