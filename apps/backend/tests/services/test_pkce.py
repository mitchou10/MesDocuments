import base64
import hashlib

from app.services.pkce import generate_pkce_pair


def test_generate_pkce_pair_produces_matching_s256_challenge():
    verifier, challenge = generate_pkce_pair()

    expected_digest = hashlib.sha256(verifier.encode("ascii")).digest()
    expected_challenge = base64.urlsafe_b64encode(expected_digest).rstrip(b"=").decode("ascii")

    assert challenge == expected_challenge
    # No padding, no '+' or '/': must be URL-safe as required by RFC 7636.
    assert "=" not in challenge
    assert "+" not in challenge
    assert "/" not in challenge


def test_generate_pkce_pair_is_random():
    verifier_a, challenge_a = generate_pkce_pair()
    verifier_b, challenge_b = generate_pkce_pair()

    assert verifier_a != verifier_b
    assert challenge_a != challenge_b
