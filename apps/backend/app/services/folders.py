import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from app.db.models.folders import Folder
from app.repositories.folders import FolderRepository
from app.repositories.pagination import Page
from app.schemas.pagination import PageParams


class FolderNotFoundError(Exception):
    def __init__(self, folder_id: uuid.UUID) -> None:
        self.folder_id = folder_id
        super().__init__(f"Folder {folder_id} not found")


class InvalidFolderNameError(Exception):
    pass


@dataclass
class FolderTree:
    folder: Folder | None
    subfolders: Page[Folder]


class FolderService:
    """Business rules around folders: name validation, existence checks,
    breadcrumb computation. Delegates all actual storage to `FolderRepository`.
    """

    def __init__(self, repository: FolderRepository) -> None:
        self._repository = repository

    async def get_folder(self, folder_id: uuid.UUID) -> Folder:
        folder = await self._repository.get(folder_id)
        if folder is None or folder.deleted_at is not None:
            raise FolderNotFoundError(folder_id)
        return folder

    async def get_children(self, parent_id: uuid.UUID | None, page: PageParams) -> FolderTree:
        folder = await self.get_folder(parent_id) if parent_id is not None else None
        subfolders = await self._repository.get_children(parent_id, page)
        return FolderTree(folder=folder, subfolders=subfolders)

    async def list_folders_for_user(self, owner_id: uuid.UUID, page: PageParams) -> Page[Folder]:
        return await self._repository.list_by_owner(owner_id, page)

    async def list_root_folders_for_user(self, owner_id: uuid.UUID, page: PageParams) -> Page[Folder]:
        return await self._repository.get_root_folders_for_owner(owner_id, page)

    async def get_path(self, folder_id: uuid.UUID) -> list[Folder]:
        """Root-to-parent chain (excludes the folder itself) - for breadcrumbs."""
        path: list[Folder] = []
        current = await self.get_folder(folder_id)
        while current.parent_id is not None:
            current = await self.get_folder(current.parent_id)
            path.append(current)
        path.reverse()
        return path

    async def create_folder(self, *, name: str, parent_id: uuid.UUID | None, owner_id: uuid.UUID) -> Folder:
        name = self._validate_name(name)
        if parent_id is not None:
            await self.get_folder(parent_id)  # raises FolderNotFoundError if missing/deleted
        return await self._repository.create(name=name, parent_id=parent_id, owner_id=owner_id)

    async def rename_folder(self, folder_id: uuid.UUID, name: str) -> Folder:
        name = self._validate_name(name)
        folder = await self.get_folder(folder_id)
        return await self._repository.rename(folder, name)

    async def delete_folder(self, folder_id: uuid.UUID) -> None:
        folder = await self.get_folder(folder_id)
        await self._repository.soft_delete(folder, deleted_at=datetime.now(UTC))

    @staticmethod
    def _validate_name(name: str) -> str:
        name = name.strip()
        if not name:
            raise InvalidFolderNameError("Folder name cannot be empty")
        return name
