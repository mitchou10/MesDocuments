import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin
from app.db.models.enums import AgentMessageRole


class AgentConversation(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "agent_conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    scope: Mapped[dict] = mapped_column(JSONB)  # {"type": "file"|"folder"|"all", "id": ..., "recursive": ...}
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AgentMessage(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "agent_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_conversations.id")
    )
    role: Mapped[AgentMessageRole] = mapped_column(Enum(AgentMessageRole, name="agent_message_role"))
    text: Mapped[str]
    sources: Mapped[list | None] = mapped_column(JSONB)
    activities: Mapped[list | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
