from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MESDOCUMENTS_", env_file=".env", extra="ignore")

    # Doit correspondre exactement au claim "iss" des tokens émis par Keycloak
    # (fixé par KC_HOSTNAME côté Keycloak) : c'est aussi l'URL publique que le
    # navigateur utilise pour les redirections /auth et /logout.
    keycloak_issuer: str = "http://localhost:8080/realms/mesdocuments"
    # Chemins réseau utilisés par le backend pour parler à Keycloak *sans*
    # passer par le navigateur (JWKS, échange de code, refresh). En Docker
    # Compose ce n'est pas le même hôte que `keycloak_issuer` (ex: "keycloak"
    # sur le réseau interne vs "localhost" côté navigateur). Si absent, on
    # retombe sur `keycloak_issuer`.
    keycloak_jwks_base_url: str | None = None
    keycloak_token_base_url: str | None = None

    keycloak_client_id: str = "mesdocuments-backend"
    keycloak_client_secret: str = "dev-secret-change-me"
    keycloak_audience: str = "mesdocuments-backend"

    # Adresse *publique* (vue par le navigateur) du callback OAuth du backend.
    # Passe par le proxy Vite du frontend pour rester same-origin avec le SPA,
    # ce qui évite tout problème de cookie cross-site en dev.
    keycloak_redirect_uri: str = "http://localhost:5173/api/v1/auth/callback"
    frontend_base_url: str = "http://localhost:5173"

    session_cookie_name: str = "mesdocuments_session"
    session_ttl_seconds: int = 8 * 60 * 60

    cors_origins: list[str] = ["http://localhost:5173"]

    database_url: str = "postgresql+asyncpg://mesdocuments:mesdocuments@localhost:5432/mesdocuments"

    # File bytes are proxied through the backend (chunked, streamed - see
    # app/services/storage.py), never served directly from MinIO to the
    # browser, so there's no public/internal endpoint split to worry about
    # here (unlike Keycloak).
    minio_endpoint: str = "http://localhost:9000"
    minio_access_key: str = "mesdocuments"
    minio_secret_key: str = "mesdocuments123"
    minio_bucket: str = "mesdocuments-files"

    @property
    def keycloak_jwks_url(self) -> str:
        base = self.keycloak_jwks_base_url or self.keycloak_issuer
        return f"{base}/protocol/openid-connect/certs"

    @property
    def keycloak_token_url(self) -> str:
        base = self.keycloak_token_base_url or self.keycloak_issuer
        return f"{base}/protocol/openid-connect/token"

    @property
    def keycloak_authorization_url(self) -> str:
        return f"{self.keycloak_issuer}/protocol/openid-connect/auth"

    @property
    def keycloak_logout_url(self) -> str:
        return f"{self.keycloak_issuer}/protocol/openid-connect/logout"


@lru_cache
def get_settings() -> Settings:
    return Settings()
