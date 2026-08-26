import time
from dataclasses import dataclass, field

from app.schemas.auth import CurrentUser


@dataclass
class Session:
    user: CurrentUser
    access_token: str
    refresh_token: str | None
    id_token: str | None
    expires_at: float


@dataclass
class PendingLogin:
    code_verifier: str
    return_to: str
    created_at: float = field(default_factory=time.time)


_PENDING_LOGIN_TTL_SECONDS = 5 * 60


class SessionStore:
    """In-memory session storage.

    Fine for a single-process dev/demo backend. A real deployment would swap
    this for Redis (or another shared store) without touching the router.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._pending_logins: dict[str, PendingLogin] = {}

    def create_session(self, session_id: str, session: Session) -> None:
        self._sessions[session_id] = session

    def get_session(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def start_login(self, state: str, pending: PendingLogin) -> None:
        self._evict_expired_pending_logins()
        self._pending_logins[state] = pending

    def pop_pending_login(self, state: str) -> PendingLogin | None:
        return self._pending_logins.pop(state, None)

    def _evict_expired_pending_logins(self) -> None:
        now = time.time()
        expired = [
            state
            for state, pending in self._pending_logins.items()
            if now - pending.created_at > _PENDING_LOGIN_TTL_SECONDS
        ]
        for state in expired:
            self._pending_logins.pop(state, None)


_store: SessionStore | None = None


def get_session_store() -> SessionStore:
    global _store
    if _store is None:
        _store = SessionStore()
    return _store
