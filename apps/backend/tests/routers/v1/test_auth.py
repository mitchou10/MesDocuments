import time
from urllib.parse import parse_qs, urlparse

import app.services.oauth_client as oauth_client_module
from app.services.sessions import Session
from tests.conftest import COOKIE_NAME, make_current_user, make_token


def test_health_is_public(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_me_requires_a_session(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_returns_claims_for_a_valid_session(client, fresh_session_store):
    session_id = "session-abc"
    fresh_session_store.create_session(
        session_id,
        Session(
            user=make_current_user(),
            access_token="irrelevant",
            refresh_token=None,
            id_token=None,
            expires_at=time.time() + 300,
        ),
    )

    response = client.get("/api/v1/auth/me", cookies={COOKIE_NAME: session_id})

    assert response.status_code == 200
    body = response.json()
    assert body["sub"] == "user-123"
    assert body["username"] == "camille"
    assert body["roles"] == ["user"]


def test_me_rejects_unknown_session(client):
    response = client.get("/api/v1/auth/me", cookies={COOKIE_NAME: "does-not-exist"})
    assert response.status_code == 401


def test_login_redirects_to_keycloak_with_pkce(client):
    response = client.get("/api/v1/auth/login?return_to=/documents", follow_redirects=False)

    assert response.status_code == 302
    location = urlparse(response.headers["location"])
    query = parse_qs(location.query)
    assert location.netloc == "localhost:8080"
    assert query["client_id"] == ["mesdocuments-backend"]
    assert query["code_challenge_method"] == ["S256"]
    assert "code_challenge" in query
    assert "state" in query


def test_callback_rejects_unknown_state(client):
    response = client.get("/api/v1/auth/callback?code=abc&state=unknown", follow_redirects=False)
    assert response.status_code == 400


def test_callback_creates_session_and_redirects(client, rsa_keypair, monkeypatch):
    private_key, _ = rsa_keypair
    login_response = client.get("/api/v1/auth/login?return_to=/documents", follow_redirects=False)
    state = parse_qs(urlparse(login_response.headers["location"]).query)["state"][0]

    token = make_token(private_key)

    async def _fake_exchange_code(self, code, code_verifier):
        assert code == "auth-code"
        assert code_verifier
        return {
            "access_token": token,
            "refresh_token": "refresh-abc",
            "id_token": "id-abc",
            "expires_in": 300,
        }

    monkeypatch.setattr(oauth_client_module.KeycloakOAuthClient, "exchange_code", _fake_exchange_code)

    response = client.get(f"/api/v1/auth/callback?code=auth-code&state={state}", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"] == "http://localhost:5173/documents"
    session_cookie = response.cookies.get(COOKIE_NAME)
    assert session_cookie is not None

    me_response = client.get("/api/v1/auth/me", cookies={COOKIE_NAME: session_cookie})
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "camille"


def test_logout_clears_session_and_redirects_to_keycloak(client, fresh_session_store):
    session_id = "session-to-clear"
    fresh_session_store.create_session(
        session_id,
        Session(
            user=make_current_user(),
            access_token="irrelevant",
            refresh_token=None,
            id_token="id-abc",
            expires_at=time.time() + 300,
        ),
    )

    response = client.get("/api/v1/auth/logout", cookies={COOKIE_NAME: session_id}, follow_redirects=False)

    assert response.status_code == 302
    assert "id_token_hint=id-abc" in response.headers["location"]
    assert fresh_session_store.get_session(session_id) is None
