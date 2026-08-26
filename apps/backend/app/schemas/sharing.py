import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.models.enums import PermissionLevel, PrincipalType, ResourceType


class ShareCreate(BaseModel):
    resource_type: ResourceType
    resource_id: uuid.UUID
    principal_type: PrincipalType
    principal_id: uuid.UUID
    level: PermissionLevel


class ShareRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resource_type: ResourceType
    resource_id: uuid.UUID
    principal_type: PrincipalType
    principal_id: uuid.UUID
    level: PermissionLevel
    created_by: uuid.UUID
    created_at: datetime


class FavoriteCreate(BaseModel):
    resource_type: ResourceType
    resource_id: uuid.UUID


class FavoriteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    resource_type: ResourceType
    resource_id: uuid.UUID
    created_at: datetime
