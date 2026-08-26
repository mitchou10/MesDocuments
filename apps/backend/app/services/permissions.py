import uuid

from app.db.models.enums import PermissionLevel, PrincipalType, ResourceType
from app.db.models.folders import Folder
from app.db.models.sharing import Share
from app.repositories.folders import FolderRepository
from app.repositories.groups import GroupRepository
from app.repositories.shares import ShareRepository


class AccessDeniedError(Exception):
    def __init__(self, resource_id: uuid.UUID) -> None:
        self.resource_id = resource_id
        super().__init__(f"Access denied to {resource_id}")


class FolderPermissionService:
    """Resolves whether a user can read/edit a folder.

    Access comes from exactly two places: ownership, or a `Share` on the
    folder itself or one of its ancestors (a share on a parent folder grants
    the same level on everything under it - there is no separate "denied"
    grant type; not owning the resource and finding no share anywhere up the
    chain simply means no access).
    """

    def __init__(
        self,
        folder_repository: FolderRepository,
        share_repository: ShareRepository,
        group_repository: GroupRepository,
    ) -> None:
        self._folders = folder_repository
        self._shares = share_repository
        self._groups = group_repository

    async def get_access_level(self, user_id: uuid.UUID, folder: Folder) -> PermissionLevel | None:
        if folder.owner_id == user_id:
            return PermissionLevel.editor

        group_ids = await self._groups.get_group_ids_for_user(user_id)

        current: Folder | None = folder
        while current is not None:
            shares = await self._shares.list_for_resource(ResourceType.folder, current.id)
            level = self._best_level(shares, user_id, group_ids)
            if level is not None:
                return level
            current = await self._folders.get(current.parent_id) if current.parent_id is not None else None
            if current is not None and current.deleted_at is not None:
                return None

        return None

    async def require_access(
        self, user_id: uuid.UUID, folder: Folder, minimum: PermissionLevel = PermissionLevel.reader
    ) -> None:
        level = await self.get_access_level(user_id, folder)
        if level is None:
            raise AccessDeniedError(folder.id)
        if minimum == PermissionLevel.editor and level != PermissionLevel.editor:
            raise AccessDeniedError(folder.id)

    @staticmethod
    def _best_level(
        shares: list[Share], user_id: uuid.UUID, group_ids: list[uuid.UUID]
    ) -> PermissionLevel | None:
        levels = [
            share.level
            for share in shares
            if (share.principal_type == PrincipalType.user and share.principal_id == user_id)
            or (share.principal_type == PrincipalType.group and share.principal_id in group_ids)
        ]
        if not levels:
            return None
        return PermissionLevel.editor if PermissionLevel.editor in levels else PermissionLevel.reader
