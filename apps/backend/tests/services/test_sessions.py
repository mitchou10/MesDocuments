import time

from app.services.sessions import PendingLogin, Session, SessionStore
from tests.conftest import make_current_user


def test_create_get_delete_session():
    store = SessionStore()
    session = Session(
        user=make_current_user(), access_token="a", refresh_token=None, id_token=None, expires_at=0
    )

    store.create_session("sid", session)
    assert store.get_session("sid") is session

    store.delete_session("sid")
    assert store.get_session("sid") is None


def test_get_unknown_session_returns_none():
    store = SessionStore()
    assert store.get_session("nope") is None


def test_pop_pending_login_returns_it_once():
    store = SessionStore()
    pending = PendingLogin(code_verifier="verifier", return_to="/documents")

    store.start_login("state-1", pending)

    assert store.pop_pending_login("state-1") is pending
    assert store.pop_pending_login("state-1") is None


def test_pop_pending_login_unknown_state_returns_none():
    store = SessionStore()
    assert store.pop_pending_login("unknown") is None


def test_start_login_evicts_expired_pending_logins():
    store = SessionStore()
    expired = PendingLogin(code_verifier="old", return_to="/", created_at=time.time() - 10 * 60)
    store.start_login("expired-state", expired)

    store.start_login("new-state", PendingLogin(code_verifier="new", return_to="/documents"))

    assert store.pop_pending_login("expired-state") is None
    assert store.pop_pending_login("new-state") is not None
