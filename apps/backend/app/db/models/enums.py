import enum


class ResourceType(enum.StrEnum):
    file = "file"
    folder = "folder"


class PrincipalType(enum.StrEnum):
    user = "user"
    group = "group"


class PermissionLevel(enum.StrEnum):
    reader = "reader"
    editor = "editor"


class GroupRole(enum.StrEnum):
    member = "member"
    admin = "admin"


class FileKind(enum.StrEnum):
    pdf = "pdf"
    audio = "audio"
    video = "video"
    image = "image"
    other = "other"


class AgentMessageRole(enum.StrEnum):
    user = "user"
    agent = "agent"


class TaskType(enum.StrEnum):
    file_ingestion = "file_ingestion"
    folder_summary = "folder_summary"
    reindex = "reindex"


class TaskStatus(enum.StrEnum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"
