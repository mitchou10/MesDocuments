from functools import lru_cache

import jwt

from app.config import get_settings


@lru_cache
def get_jwk_client() -> jwt.PyJWKClient:
    settings = get_settings()
    # PyJWKClient caches keys in-memory and refetches on an unknown `kid`,
    # so a realm's key rotation is picked up without restarting the service.
    return jwt.PyJWKClient(settings.keycloak_jwks_url, cache_keys=True)
