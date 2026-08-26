import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.db.models.enums import ResourceType


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: uuid.UUID | None
    action: str
    resource_type: ResourceType | None
    resource_id: uuid.UUID | None
    extra: dict[str, Any] | None
    created_at: datetime
