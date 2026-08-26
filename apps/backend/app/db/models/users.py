import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """Local shadow of a Keycloak identity.

    `id` is the Keycloak `sub` claim, not generated here - Keycloak stays the
    source of truth for auth; this row exists only so other tables have a
    stable local FK target, and to avoid round-tripping to Keycloak for
    display purposes.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    username: Mapped[str | None]
    email: Mapped[str | None]
    display_name: Mapped[str | None]
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
