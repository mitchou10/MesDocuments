from urllib.parse import urlencode

import httpx

from app.config import get_settings


class OAuthExchangeError(Exception):
    pass


class KeycloakOAuthClient:
    def build_authorization_url(self, state: str, code_challenge: str) -> str:
        settings = get_settings()
        params = {
            "client_id": settings.keycloak_client_id,
            "response_type": "code",
            "redirect_uri": settings.keycloak_redirect_uri,
            "scope": "openid profile email",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        return f"{settings.keycloak_authorization_url}?{urlencode(params)}"

    def build_logout_url(self, id_token_hint: str | None) -> str:
        settings = get_settings()
        params = {"post_logout_redirect_uri": settings.frontend_base_url}
        if id_token_hint:
            params["id_token_hint"] = id_token_hint
        return f"{settings.keycloak_logout_url}?{urlencode(params)}"

    async def exchange_code(self, code: str, code_verifier: str) -> dict:
        settings = get_settings()
        return await self._post_token(
            {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.keycloak_redirect_uri,
                "code_verifier": code_verifier,
            }
        )

    async def refresh(self, refresh_token: str) -> dict:
        return await self._post_token({"grant_type": "refresh_token", "refresh_token": refresh_token})

    async def _post_token(self, data: dict[str, str]) -> dict:
        settings = get_settings()
        payload = {
            "client_id": settings.keycloak_client_id,
            "client_secret": settings.keycloak_client_secret,
            **data,
        }
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(settings.keycloak_token_url, data=payload)
        if response.status_code != 200:
            raise OAuthExchangeError(
                f"Keycloak token endpoint returned {response.status_code}: {response.text}"
            )
        return response.json()


def get_oauth_client() -> KeycloakOAuthClient:
    return KeycloakOAuthClient()
