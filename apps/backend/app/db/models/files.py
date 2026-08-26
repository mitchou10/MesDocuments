import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.models.enums import FileKind


class File(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Stable identity + current metadata for a file.

    The "current" version is whichever `FileVersion` has the highest
    `version_number` for this `file_id` - no `current_version_id` column here,
    to avoid a circular FK between `files` and `file_versions`.
    """

    __tablename__ = "files"

    name: Mapped[str]
    kind: Mapped[FileKind] = mapped_column(Enum(FileKind, name="file_kind"))
    mime_type: Mapped[str]
    size_bytes: Mapped[int]
    folder_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("folders.id"))
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    page_count: Mapped[int | None]
    duration_ms: Mapped[int | None]
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class FileVersion(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "file_versions"
    __table_args__ = (UniqueConstraint("file_id", "version_number"),)

    file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("files.id"))
    version_number: Mapped[int]
    # Object storage (S3/MinIO) reference - never the file bytes themselves.
    storage_key: Mapped[str]
    content_hash: Mapped[str]  # sha256 hex digest: integrity check + dedup
    size_bytes: Mapped[int]
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    note: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DocumentSummary(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "document_summaries"

    file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("files.id"))
    version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("file_versions.id"))
    text: Mapped[str]
    model: Mapped[str | None]
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DocumentChunk(Base, UUIDPrimaryKeyMixin):
    """Chunk text + its source locator (page/bbox or timestamp range).

    The embedding vector itself lives in Qdrant, not here - `qdrant_point_id`
    is just the pointer to it.
    """

    __tablename__ = "document_chunks"

    file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("files.id"))
    version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("file_versions.id"))
    text: Mapped[str]
    source: Mapped[dict] = mapped_column(JSONB)
    qdrant_point_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FolderSummary(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "folder_summaries"

    folder_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("folders.id"))
    text: Mapped[str]
    recursive: Mapped[bool] = mapped_column(default=False)
    model: Mapped[str | None]
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
