from typing import Any

import jwt

from app.config import get_settings
from app.schemas.auth import CurrentUser
from app.services.jwks import get_jwk_client


def verify_access_token(token: str) -> dict[str, Any]:
    """Verifies signature, issuer, audience and expiry; returns the raw claims.

    Raises jwt.PyJWTError (or a subclass) on any validation failure.
    """
    settings = get_settings()
    signing_key = get_jwk_client().get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.keycloak_audience,
        issuer=settings.keycloak_issuer,
        options={"require": ["exp", "iat", "sub"]},
    )


def claims_to_user(claims: dict[str, Any]) -> CurrentUser:
    return CurrentUser(
        sub=claims["sub"],
        username=claims.get("preferred_username"),
        email=claims.get("email"),
        name=claims.get("name"),
        roles=claims.get("realm_access", {}).get("roles", []),
    )
