import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import PermissionLevel
from app.db.models.files import File
from app.db.models.users import User
from app.db.session import get_db
from app.dependencies.current_user import get_current_db_user
from app.dependencies.files import get_file_service
from app.dependencies.folders import get_folder_permission_service, get_folder_service
from app.routers.v1._folder_access import get_folder_or_404, require_folder_access
from app.schemas.files import FileRead, FileRename
from app.schemas.pagination import PageOut, PageParams
from app.services.files import FileNotFoundError, FileService, InvalidFileNameError
from app.services.folders import FolderService
from app.services.permissions import FolderPermissionService

router = APIRouter(tags=["files"])

# Read from the incoming multipart body in small pieces and hand each one
# straight to the storage layer - matches StorageService's own chunking, so
# nothing upstream ever holds the whole file in memory either.
_UPLOAD_READ_CHUNK = 1024 * 1024


async def _iter_upload(upload_file: UploadFile) -> AsyncIterator[bytes]:
    while chunk := await upload_file.read(_UPLOAD_READ_CHUNK):
        yield chunk


@router.post("/folders/{folder_id}/files", status_code=status.HTTP_201_CREATED)
async def upload_file(
    folder_id: uuid.UUID,
    file: UploadFile,
    name: str | None = Form(None),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_db_user),
    folder_service: FolderService = Depends(get_folder_service),
    file_service: FileService = Depends(get_file_service),
    permission_service: FolderPermissionService = Depends(get_folder_permission_service),
) -> FileRead:
    folder = await get_folder_or_404(folder_service, folder_id)
    await require_folder_access(permission_service, current_user.id, folder, PermissionLevel.editor)

    try:
        created = await file_service.upload_file(
            folder_id=folder_id,
            owner_id=current_user.id,
            filename=name or file.filename or "sans-nom",
            content_type=file.content_type,
            stream=_iter_upload(file),
        )
    except InvalidFileNameError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    await session.commit()
    return FileRead.model_validate(created)


@router.get("/folders/{folder_id}/files")
async def list_files(
    folder_id: uuid.UUID,
    page: PageParams = Depends(),
    current_user: User = Depends(get_current_db_user),
    folder_service: FolderService = Depends(get_folder_service),
    file_service: FileService = Depends(get_file_service),
    permission_service: FolderPermissionService = Depends(get_folder_permission_service),
) -> PageOut[FileRead]:
    folder = await get_folder_or_404(folder_service, folder_id)
    await require_folder_access(permission_service, current_user.id, folder, PermissionLevel.reader)

    result = await file_service.get_children(folder_id, page)
    return PageOut.from_page(result, FileRead)


@router.get("/files/{file_id}")
async def get_file(
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_db_user),
    folder_service: FolderService = Depends(get_folder_service),
    file_service: FileService = Depends(get_file_service),
    permission_service: FolderPermissionService = Depends(get_folder_permission_service),
) -> FileRead:
    file = await _get_file_and_check_access(
        file_id, PermissionLevel.reader, current_user, folder_service, file_service, permission_service
    )
    return FileRead.model_validate(file)


@router.get("/files/{file_id}/download")
async def download_file(
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_db_user),
    folder_service: FolderService = Depends(get_folder_service),
    file_service: FileService = Depends(get_file_service),
    permission_service: FolderPermissionService = Depends(get_folder_permission_service),
) -> StreamingResponse:
    await _get_file_and_check_access(
        file_id, PermissionLevel.reader, current_user, folder_service, file_service, permission_service
    )
    file, stream = await file_service.download_file(file_id)
    return StreamingResponse(
        stream,
        media_type=file.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{file.name}"'},
    )


@router.patch("/files/{file_id}")
async def rename_file(
    file_id: uuid.UUID,
    payload: FileRename,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_db_user),
    folder_service: FolderService = Depends(get_folder_service),
    file_service: FileService = Depends(get_file_service),
    permission_service: FolderPermissionService = Depends(get_folder_permission_service),
) -> FileRead:
    await _get_file_and_check_access(
        file_id, PermissionLevel.editor, current_user, folder_service, file_service, permission_service
    )
    try:
        file = await file_service.rename_file(file_id, payload.name)
    except InvalidFileNameError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    await session.commit()
    return FileRead.model_validate(file)


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_db_user),
    folder_service: FolderService = Depends(get_folder_service),
    file_service: FileService = Depends(get_file_service),
    permission_service: FolderPermissionService = Depends(get_folder_permission_service),
) -> None:
    await _get_file_and_check_access(
        file_id, PermissionLevel.editor, current_user, folder_service, file_service, permission_service
    )
    await file_service.delete_file(file_id)
    await session.commit()


async def _get_file_and_check_access(
    file_id: uuid.UUID,
    minimum: PermissionLevel,
    current_user: User,
    folder_service: FolderService,
    file_service: FileService,
    permission_service: FolderPermissionService,
) -> File:
    try:
        file = await file_service.get_file(file_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found") from exc

    folder = await get_folder_or_404(folder_service, file.folder_id)
    await require_folder_access(permission_service, current_user.id, folder, minimum)
    return file
