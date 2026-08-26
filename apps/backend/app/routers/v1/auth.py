import secrets
import time

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.config import get_settings
from app.dependencies.auth import get_current_user
from app.schemas.auth import CurrentUser
from app.services.oauth_client import KeycloakOAuthClient, OAuthExchangeError, get_oauth_client
from app.services.pkce import generate_pkce_pair
from app.services.sessions import PendingLogin, Session, SessionStore, get_session_store
from app.services.token_verifier import claims_to_user, verify_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
def login(
    return_to: str = "/",
    store: SessionStore = Depends(get_session_store),
    oauth_client: KeycloakOAuthClient = Depends(get_oauth_client),
) -> RedirectResponse:
    code_verifier, code_challenge = generate_pkce_pair()
    state = secrets.token_urlsafe(32)
    store.start_login(state, PendingLogin(code_verifier=code_verifier, return_to=return_to))

    authorization_url = oauth_client.build_authorization_url(state=state, code_challenge=code_challenge)
    return RedirectResponse(authorization_url, status_code=status.HTTP_302_FOUND)


@router.get("/callback")
async def callback(
    code: str,
    state: str,
    store: SessionStore = Depends(get_session_store),
    oauth_client: KeycloakOAuthClient = Depends(get_oauth_client),
) -> RedirectResponse:
    pending = store.pop_pending_login(state)
    if pending is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown or expired login attempt"
        )

    try:
        tokens = await oauth_client.exchange_code(code=code, code_verifier=pending.code_verifier)
        claims = verify_access_token(tokens["access_token"])
    except (OAuthExchangeError, jwt.PyJWTError, KeyError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login failed") from exc

    settings = get_settings()
    session_id = secrets.token_urlsafe(32)
    store.create_session(
        session_id,
        Session(
            user=claims_to_user(claims),
            access_token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token"),
            id_token=tokens.get("id_token"),
            expires_at=time.time() + tokens.get("expires_in", 300),
        ),
    )

    response = RedirectResponse(
        f"{settings.frontend_base_url}{pending.return_to}", status_code=status.HTTP_302_FOUND
    )
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=False,  # dev only: no TLS on localhost. Set True behind HTTPS.
        max_age=settings.session_ttl_seconds,
        path="/",
    )
    return response


@router.get("/me")
def read_current_user(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return current_user


@router.get("/logout")
def logout(
    request: Request,
    store: SessionStore = Depends(get_session_store),
    oauth_client: KeycloakOAuthClient = Depends(get_oauth_client),
) -> RedirectResponse:
    settings = get_settings()
    session_id = request.cookies.get(settings.session_cookie_name)
    id_token_hint = None
    if session_id:
        session = store.get_session(session_id)
        id_token_hint = session.id_token if session else None
        store.delete_session(session_id)

    logout_url = oauth_client.build_logout_url(id_token_hint=id_token_hint)
    response = RedirectResponse(logout_url, status_code=status.HTTP_302_FOUND)
    response.delete_cookie(settings.session_cookie_name, path="/")
    return response
