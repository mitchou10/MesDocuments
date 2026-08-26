import time
import uuid

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.services.token_verifier as token_verifier
from app.config import get_settings
from app.db.base import Base
from app.db.models.users import User
from app.main import app
from app.schemas.auth import CurrentUser
from app.services.sessions import get_session_store

# Real Postgres, not sqlite: the models use Postgres-specific types (native
# UUID, JSONB, server-side ENUMs) that sqlite can't represent. Matches
# docker-compose.yml's `postgres` service - run `docker compose up -d
# postgres` before running DB-backed tests.
#
# A DEDICATED database, not the dev one: this suite runs
# `Base.metadata.create_all`/`drop_all` around every test, which would wipe
# real dev data if pointed at the same `mesdocuments` database. See
# `infra/postgres/init-test-db.sql`.
TEST_DATABASE_URL = "postgresql+asyncpg://mesdocuments:mesdocuments@localhost:5432/mesdocuments_test"

ISSUER = "http://localhost:8080/realms/mesdocuments"
AUDIENCE = "mesdocuments-backend"
COOKIE_NAME = "mesdocuments_session"


@pytest.fixture(autouse=True)
def _settings_env(monkeypatch):
    monkeypatch.setenv("MESDOCUMENTS_KEYCLOAK_ISSUER", ISSUER)
    monkeypatch.setenv("MESDOCUMENTS_KEYCLOAK_AUDIENCE", AUDIENCE)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def fresh_session_store():
    # The store is a process-wide singleton; give every test a clean slate.
    store = get_session_store()
    store._sessions.clear()
    store._pending_logins.clear()
    yield store


@pytest.fixture
def rsa_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


class FakeSigningKey:
    def __init__(self, key):
        self.key = key


class FakeJwkClient:
    def __init__(self, public_key):
        self._public_key = public_key

    def get_signing_key_from_jwt(self, token):
        return FakeSigningKey(self._public_key)


@pytest.fixture
def client(rsa_keypair, monkeypatch):
    _, public_key = rsa_keypair
    monkeypatch.setattr(token_verifier, "get_jwk_client", lambda: FakeJwkClient(public_key))
    return TestClient(app)


def make_token(private_key, **overrides) -> str:
    now = int(time.time())
    payload = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": "user-123",
        "iat": now,
        "exp": now + 300,
        "preferred_username": "camille",
        "email": "camille.bernard@example.fr",
        "name": "Camille Bernard",
        "realm_access": {"roles": ["user"]},
        **overrides,
    }
    return jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": "test-key"})


def make_current_user() -> CurrentUser:
    return CurrentUser(
        sub="user-123",
        username="camille",
        email="camille.bernard@example.fr",
        name="Camille Bernard",
        roles=["user"],
    )


@pytest.fixture
async def db_session():
    """A real async session against a freshly-created schema.

    `create_all`/`drop_all` (not Alembic) on purpose: fast, and the point of
    these tests is exercising repositories/services, not the migration
    itself - that already has its own upgrade/downgrade verification.
    """
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def make_user(db_session: AsyncSession):
    async def _make_user(**overrides) -> User:
        defaults = {"id": uuid.uuid4(), "username": "camille", "email": "camille@example.fr"}
        user = User(**{**defaults, **overrides})
        db_session.add(user)
        await db_session.flush()
        return user

    return _make_user
