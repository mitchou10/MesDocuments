import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.models.enums import GroupRole


class GroupCreate(BaseModel):
    name: str


class GroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    created_by: uuid.UUID | None
    created_at: datetime


class GroupMemberCreate(BaseModel):
    user_id: uuid.UUID
    role: GroupRole = GroupRole.member


class GroupMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    group_id: uuid.UUID
    user_id: uuid.UUID
    role: GroupRole
    joined_at: datetime
