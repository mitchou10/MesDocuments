import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.db.models.enums import AgentMessageRole
from app.schemas.files import DocumentSource


class AgentConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    scope: dict[str, Any]
    created_at: datetime


class AgentMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    role: AgentMessageRole
    text: str
    sources: list[DocumentSource] | None
    activities: list[dict[str, Any]] | None
    created_at: datetime
