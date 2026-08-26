"""Import every model so `Base.metadata` is complete - required for Alembic
autogenerate to see all tables once migrations are wired up."""

from app.db.models.agent import AgentConversation, AgentMessage
from app.db.models.audit import AuditLog
from app.db.models.files import DocumentChunk, DocumentSummary, File, FileVersion, FolderSummary
from app.db.models.folders import Folder
from app.db.models.groups import Group, GroupMember
from app.db.models.sharing import Favorite, Share
from app.db.models.tasks import Task
from app.db.models.users import User

__all__ = [
    "AgentConversation",
    "AgentMessage",
    "AuditLog",
    "DocumentChunk",
    "DocumentSummary",
    "File",
    "FileVersion",
    "Favorite",
    "Folder",
    "FolderSummary",
    "Group",
    "GroupMember",
    "Share",
    "Task",
    "User",
]
