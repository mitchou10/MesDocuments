import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.models.enums import ResourceType, TaskStatus, TaskType


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: TaskType
    status: TaskStatus
    progress: int
    resource_type: ResourceType | None
    resource_id: uuid.UUID | None
    error_message: str | None
    created_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
