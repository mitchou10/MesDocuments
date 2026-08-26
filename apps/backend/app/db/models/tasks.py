import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin
from app.db.models.enums import ResourceType, TaskStatus, TaskType


class Task(Base, UUIDPrimaryKeyMixin):
    """Background job tracking (upload ingestion, folder summaries, reindex...).

    Mirrors the frontend's simulated upload pipeline: selected -> uploading ->
    processing -> done/error, driven here by `status` + `progress`.
    """

    __tablename__ = "tasks"
    __table_args__ = (CheckConstraint("progress >= 0 AND progress <= 100", name="progress_range"),)

    type: Mapped[TaskType] = mapped_column(Enum(TaskType, name="task_type"))
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status"), default=TaskStatus.pending
    )
    progress: Mapped[int] = mapped_column(default=0)  # 0-100
    resource_type: Mapped[ResourceType | None] = mapped_column(Enum(ResourceType, name="resource_type"))
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    error_message: Mapped[str | None]
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
