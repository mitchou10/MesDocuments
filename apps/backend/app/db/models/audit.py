import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.enums import ResourceType


class AuditLog(Base):
    """Who did what, when. Append-only: never updated or deleted.

    A plain autoincrementing bigint PK (not UUID) - audit rows are written
    far more than read, and their natural order matters more than opacity.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    action: Mapped[str]  # e.g. "file.create", "share.add", "permission.revoke"
    resource_type: Mapped[ResourceType | None] = mapped_column(Enum(ResourceType, name="resource_type"))
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    extra: Mapped[dict | None] = mapped_column(JSONB)  # e.g. {"before": ..., "after": ...}
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
