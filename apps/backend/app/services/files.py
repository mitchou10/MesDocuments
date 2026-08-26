import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime

from app.db.models.enums import FileKind
from app.db.models.files import File
from app.repositories.files import FileRepository
from app.repositories.pagination import Page
from app.schemas.pagination import PageParams
from app.services.storage import StorageService

_KIND_BY_EXACT_MIME = {"application/pdf": FileKind.pdf}
_KIND_BY_MIME_PREFIX = (("audio/", FileKind.audio), ("video/", FileKind.video), ("image/", FileKind.image))


def infer_kind(mime_type: str) -> FileKind:
    if mime_type in _KIND_BY_EXACT_MIME:
        return _KIND_BY_EXACT_MIME[mime_type]
    for prefix, kind in _KIND_BY_MIME_PREFIX:
        if mime_type.startswith(prefix):
            return kind
    return FileKind.other


class FileNotFoundError(Exception):
    def __init__(self, file_id: uuid.UUID) -> None:
        self.file_id = file_id
        super().__init__(f"File {file_id} not found")


class InvalidFileNameError(Exception):
    pass


class FileService:
    def __init__(self, repository: FileRepository, storage: StorageService) -> None:
        self._repository = repository
        self._storage = storage

    async def get_file(self, file_id: uuid.UUID) -> File:
        file = await self._repository.get(file_id)
        if file is None or file.deleted_at is not None:
            raise FileNotFoundError(file_id)
        return file

    async def get_children(self, folder_id: uuid.UUID, page: PageParams) -> Page[File]:
        return await self._repository.get_children(folder_id, page)

    async def upload_file(
        self,
        *,
        folder_id: uuid.UUID,
        owner_id: uuid.UUID,
        filename: str,
        content_type: str | None,
        stream: AsyncIterator[bytes],
    ) -> File:
        filename = self._validate_name(filename)
        file_id = uuid.uuid4()
        storage_key = f"{file_id}/v1/{filename}"

        # Streamed and chunked end to end: `stream` is read piece by piece
        # from the incoming request and pushed straight to storage - the
        # full file is never held in memory at once (see StorageService).
        size_bytes, content_hash = await self._storage.upload_stream(storage_key, stream)

        kind = infer_kind(content_type or "")
        file = await self._repository.create(
            id=file_id,
            name=filename,
            kind=kind,
            mime_type=content_type or "application/octet-stream",
            size_bytes=size_bytes,
            folder_id=folder_id,
            owner_id=owner_id,
        )
        await self._repository.create_version(
            file_id=file_id,
            version_number=1,
            storage_key=storage_key,
            content_hash=content_hash,
            size_bytes=size_bytes,
            author_id=owner_id,
        )
        return file

    async def download_file(self, file_id: uuid.UUID) -> tuple[File, AsyncIterator[bytes]]:
        file = await self.get_file(file_id)
        version = await self._repository.get_latest_version(file_id)
        if version is None:
            raise FileNotFoundError(file_id)
        return file, self._storage.download_stream(version.storage_key)

    async def rename_file(self, file_id: uuid.UUID, name: str) -> File:
        name = self._validate_name(name)
        file = await self.get_file(file_id)
        return await self._repository.rename(file, name)

    async def delete_file(self, file_id: uuid.UUID) -> None:
        file = await self.get_file(file_id)
        # Soft-delete is reversible for the metadata, but the actual bytes
        # aren't kept around for every past version once a file is deleted -
        # there's no "restore" flow that would need them.
        versions = await self._repository.get_versions(file_id)
        await self._storage.delete_many([version.storage_key for version in versions])
        await self._repository.soft_delete(file, deleted_at=datetime.now(UTC))

    async def delete_files_in_folders(self, folder_ids: list[uuid.UUID]) -> None:
        """Cascade helper for folder deletion: soft-deletes (and purges the
        storage for) every file in each given folder.

        Always re-fetches page one at offset 0: each deleted file drops out
        of the `deleted_at IS NULL` filter, so the "first page" keeps
        surfacing whatever's left instead of drifting past unprocessed rows
        the way advancing the offset while deleting would.
        """
        for folder_id in folder_ids:
            while True:
                page = await self._repository.get_children(folder_id, PageParams(limit=100))
                if not page.items:
                    break
                for file in page.items:
                    await self.delete_file(file.id)

    @staticmethod
    def _validate_name(name: str) -> str:
        name = name.strip()
        if not name:
            raise InvalidFileNameError("File name cannot be empty")
        return name
