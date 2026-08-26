import time

import jwt
from fastapi import Depends, HTTPException, Request, status

from app.config import get_settings
from app.schemas.auth import CurrentUser
from app.services.oauth_client import KeycloakOAuthClient, OAuthExchangeError, get_oauth_client
from app.services.sessions import Session, SessionStore, get_session_store
from app.services.token_verifier import claims_to_user, verify_access_token


async def get_current_user(
    request: Request,
    store: SessionStore = Depends(get_session_store),
    oauth_client: KeycloakOAuthClient = Depends(get_oauth_client),
) -> CurrentUser:
    settings = get_settings()
    session_id = request.cookies.get(settings.session_cookie_name)
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    session = store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    if session.expires_at <= time.time():
        session = await _try_refresh(session_id, session, store, oauth_client)

    return session.user


async def _try_refresh(
    session_id: str, session: Session, store: SessionStore, oauth_client: KeycloakOAuthClient
) -> Session:
    if not session.refresh_token:
        store.delete_session(session_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    try:
        tokens = await oauth_client.refresh(session.refresh_token)
        claims = verify_access_token(tokens["access_token"])
    except (OAuthExchangeError, jwt.PyJWTError, KeyError):
        store.delete_session(session_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired") from None

    refreshed = Session(
        user=claims_to_user(claims),
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token", session.refresh_token),
        id_token=tokens.get("id_token", session.id_token),
        expires_at=time.time() + tokens.get("expires_in", 300),
    )
    store.create_session(session_id, refreshed)
    return refreshed
