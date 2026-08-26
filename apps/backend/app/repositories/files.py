import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import FileKind
from app.db.models.files import File, FileVersion
from app.repositories.pagination import Page
from app.schemas.pagination import PageParams


class FileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, file_id: uuid.UUID) -> File | None:
        return await self._session.get(File, file_id)

    async def get_children(self, folder_id: uuid.UUID, page: PageParams) -> Page[File]:
        not_deleted = File.deleted_at.is_(None)
        condition = File.folder_id == folder_id

        count_stmt = select(func.count()).select_from(File).where(condition, not_deleted)
        total = (await self._session.execute(count_stmt)).scalar_one()

        # `.id` tiebreaker: same reasoning as FolderRepository - `name` alone
        # isn't unique, so pagination needs a fully deterministic order.
        items_stmt = (
            select(File)
            .where(condition, not_deleted)
            .order_by(File.name, File.id)
            .limit(page.limit)
            .offset(page.offset)
        )
        result = await self._session.execute(items_stmt)
        items = list(result.scalars().all())

        return Page(items=items, total=total, limit=page.limit, offset=page.offset)

    async def create(
        self,
        *,
        id: uuid.UUID,
        name: str,
        kind: FileKind,
        mime_type: str,
        size_bytes: int,
        folder_id: uuid.UUID,
        owner_id: uuid.UUID,
    ) -> File:
        file = File(
            id=id,
            name=name,
            kind=kind,
            mime_type=mime_type,
            size_bytes=size_bytes,
            folder_id=folder_id,
            owner_id=owner_id,
        )
        self._session.add(file)
        await self._session.flush()
        return file

    async def create_version(
        self,
        *,
        file_id: uuid.UUID,
        version_number: int,
        storage_key: str,
        content_hash: str,
        size_bytes: int,
        author_id: uuid.UUID,
        note: str | None = None,
    ) -> FileVersion:
        version = FileVersion(
            file_id=file_id,
            version_number=version_number,
            storage_key=storage_key,
            content_hash=content_hash,
            size_bytes=size_bytes,
            author_id=author_id,
            note=note,
        )
        self._session.add(version)
        await self._session.flush()
        return version

    async def get_versions(self, file_id: uuid.UUID) -> list[FileVersion]:
        stmt = (
            select(FileVersion)
            .where(FileVersion.file_id == file_id)
            .order_by(FileVersion.version_number.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_version(self, file_id: uuid.UUID) -> FileVersion | None:
        stmt = (
            select(FileVersion)
            .where(FileVersion.file_id == file_id)
            .order_by(FileVersion.version_number.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def rename(self, file: File, name: str) -> File:
        file.name = name
        await self._session.flush()
        await self._session.refresh(file)
        return file

    async def soft_delete(self, file: File, *, deleted_at: datetime) -> None:
        file.deleted_at = deleted_at
        await self._session.flush()
        await self._session.refresh(file)
