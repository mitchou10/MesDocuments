import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin
from app.db.models.enums import PermissionLevel, PrincipalType, ResourceType


class Share(Base, UUIDPrimaryKeyMixin):
    """A direct grant - the only permission data actually stored.

    "Inherited" / "denied" (as shown in the frontend) are computed at query
    time by walking the folder hierarchy, never persisted here.
    """

    __tablename__ = "shares"

    resource_type: Mapped[ResourceType] = mapped_column(Enum(ResourceType, name="resource_type"))
    resource_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    principal_type: Mapped[PrincipalType] = mapped_column(Enum(PrincipalType, name="principal_type"))
    principal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    level: Mapped[PermissionLevel] = mapped_column(Enum(PermissionLevel, name="permission_level"))
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Favorite(Base):
    __tablename__ = "favorites"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    resource_type: Mapped[ResourceType] = mapped_column(
        Enum(ResourceType, name="resource_type"), primary_key=True
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
