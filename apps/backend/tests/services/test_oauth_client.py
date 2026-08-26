from urllib.parse import parse_qs, urlparse

from app.services.oauth_client import KeycloakOAuthClient


def test_build_authorization_url_contains_pkce_and_redirect():
    client = KeycloakOAuthClient()

    url = client.build_authorization_url(state="state-123", code_challenge="challenge-abc")

    parsed = urlparse(url)
    assert parsed.netloc == "localhost:8080"
    assert parsed.path == "/realms/mesdocuments/protocol/openid-connect/auth"
    query = parse_qs(parsed.query)
    assert query["client_id"] == ["mesdocuments-backend"]
    assert query["response_type"] == ["code"]
    assert query["state"] == ["state-123"]
    assert query["code_challenge"] == ["challenge-abc"]
    assert query["code_challenge_method"] == ["S256"]
    assert query["redirect_uri"] == ["http://localhost:5173/api/v1/auth/callback"]


def test_build_logout_url_without_id_token_hint():
    client = KeycloakOAuthClient()

    url = client.build_logout_url(id_token_hint=None)

    query = parse_qs(urlparse(url).query)
    assert query["post_logout_redirect_uri"] == ["http://localhost:5173"]
    assert "id_token_hint" not in query


def test_build_logout_url_with_id_token_hint():
    client = KeycloakOAuthClient()

    url = client.build_logout_url(id_token_hint="the-id-token")

    query = parse_qs(urlparse(url).query)
    assert query["id_token_hint"] == ["the-id-token"]
