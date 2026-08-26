import base64
import hashlib
import secrets


def generate_pkce_pair() -> tuple[str, str]:
    """Returns (code_verifier, code_challenge) for an S256 PKCE exchange."""
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge
