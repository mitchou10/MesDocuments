import time

import pytest
from fastapi import HTTPException
from starlette.requests import Request

import app.services.token_verifier as token_verifier
from app.dependencies.auth import get_current_user
from app.services.oauth_client import OAuthExchangeError
from app.services.sessions import Session, SessionStore
from tests.conftest import FakeJwkClient, make_current_user, make_token

COOKIE_NAME = "mesdocuments_session"


class FakeOAuthClient:
    def __init__(self, tokens: dict | None = None, error: Exception | None = None):
        self._tokens = tokens
        self._error = error

    async def refresh(self, refresh_token: str) -> dict:
        if self._error:
            raise self._error
        return self._tokens


def build_request(cookie_value: str | None) -> Request:
    headers = []
    if cookie_value is not None:
        headers.append((b"cookie", f"{COOKIE_NAME}={cookie_value}".encode()))
    return Request({"type": "http", "headers": headers, "method": "GET", "path": "/"})


async def test_missing_cookie_raises_401():
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(build_request(None), SessionStore(), FakeOAuthClient())

    assert exc_info.value.status_code == 401


async def test_unknown_session_raises_401():
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(build_request("does-not-exist"), SessionStore(), FakeOAuthClient())

    assert exc_info.value.status_code == 401


async def test_valid_session_returns_its_user():
    store = SessionStore()
    user = make_current_user()
    store.create_session(
        "sid",
        Session(user=user, access_token="a", refresh_token=None, id_token=None, expires_at=time.time() + 300),
    )

    result = await get_current_user(build_request("sid"), store, FakeOAuthClient())

    assert result == user


async def test_expired_session_without_refresh_token_raises_401():
    store = SessionStore()
    store.create_session(
        "sid",
        Session(
            user=make_current_user(),
            access_token="a",
            refresh_token=None,
            id_token=None,
            expires_at=time.time() - 1,
        ),
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(build_request("sid"), store, FakeOAuthClient())

    assert exc_info.value.status_code == 401
    assert store.get_session("sid") is None


async def test_expired_session_is_refreshed_transparently(rsa_keypair, monkeypatch):
    private_key, public_key = rsa_keypair
    monkeypatch.setattr(token_verifier, "get_jwk_client", lambda: FakeJwkClient(public_key))

    store = SessionStore()
    store.create_session(
        "sid",
        Session(
            user=make_current_user(),
            access_token="stale",
            refresh_token="refresh-token",
            id_token="old-id-token",
            expires_at=time.time() - 1,
        ),
    )
    new_access_token = make_token(private_key, preferred_username="camille")
    oauth_client = FakeOAuthClient(
        tokens={"access_token": new_access_token, "refresh_token": "new-refresh-token", "expires_in": 300}
    )

    result = await get_current_user(build_request("sid"), store, oauth_client)

    assert result.username == "camille"
    refreshed = store.get_session("sid")
    assert refreshed.access_token == new_access_token
    assert refreshed.refresh_token == "new-refresh-token"
    assert refreshed.expires_at > time.time()


async def test_refresh_failure_deletes_session_and_raises_401():
    store = SessionStore()
    store.create_session(
        "sid",
        Session(
            user=make_current_user(),
            access_token="stale",
            refresh_token="refresh-token",
            id_token=None,
            expires_at=time.time() - 1,
        ),
    )
    oauth_client = FakeOAuthClient(error=OAuthExchangeError("boom"))

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(build_request("sid"), store, oauth_client)

    assert exc_info.value.status_code == 401
    assert store.get_session("sid") is None
