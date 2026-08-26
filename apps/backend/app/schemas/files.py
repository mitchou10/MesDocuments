import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.enums import FileKind


class PdfSource(BaseModel):
    type: Literal["pdf"] = "pdf"
    page: int
    bbox: tuple[float, float, float, float] | None = None


class AudioSource(BaseModel):
    type: Literal["audio"] = "audio"
    start_ms: int
    end_ms: int


class VideoSource(BaseModel):
    type: Literal["video"] = "video"
    start_ms: int
    end_ms: int


DocumentSource = Annotated[PdfSource | AudioSource | VideoSource, Field(discriminator="type")]


class FileCreate(BaseModel):
    name: str
    kind: FileKind
    mime_type: str
    size_bytes: int
    folder_id: uuid.UUID
    page_count: int | None = None
    duration_ms: int | None = None


class FileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    kind: FileKind
    mime_type: str
    size_bytes: int
    folder_id: uuid.UUID
    owner_id: uuid.UUID
    page_count: int | None
    duration_ms: int | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class FileRename(BaseModel):
    name: str


class FileVersionCreate(BaseModel):
    storage_key: str
    content_hash: str
    size_bytes: int
    note: str | None = None


class FileVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    file_id: uuid.UUID
    version_number: int
    storage_key: str
    content_hash: str
    size_bytes: int
    author_id: uuid.UUID
    note: str | None
    created_at: datetime


class DocumentSummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    file_id: uuid.UUID
    version_id: uuid.UUID | None
    text: str
    model: str | None
    generated_at: datetime


class DocumentChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    file_id: uuid.UUID
    version_id: uuid.UUID | None
    text: str
    source: DocumentSource
    qdrant_point_id: uuid.UUID | None
    created_at: datetime
