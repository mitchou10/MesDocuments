import uuid

from app.repositories.users import UserRepository


async def test_get_existing_user(db_session, make_user):
    user = await make_user()
    repo = UserRepository(db_session)

    fetched = await repo.get(user.id)

    assert fetched is not None
    assert fetched.id == user.id


async def test_get_returns_none_when_missing(db_session):
    repo = UserRepository(db_session)

    assert await repo.get(uuid.uuid4()) is None


async def test_upsert_creates_then_updates(db_session):
    repo = UserRepository(db_session)
    user_id = uuid.uuid4()

    created = await repo.upsert(
        id=user_id, username="camille", email="camille@example.fr", display_name="Camille"
    )
    updated = await repo.upsert(
        id=user_id, username="camille2", email="camille2@example.fr", display_name="Camille B."
    )

    assert created.id == updated.id
    assert updated.username == "camille2"


async def test_search_matches_username_display_name_or_email(db_session, make_user):
    await make_user(
        id=uuid.uuid4(),
        username="camille.bernard",
        email="camille@example.fr",
        display_name="Camille Bernard",
    )
    await make_user(id=uuid.uuid4(), username="bob.martin", email="bob@example.fr", display_name="Bob Martin")
    repo = UserRepository(db_session)

    by_username = await repo.search("camille")
    by_display_name = await repo.search("Martin")
    by_email = await repo.search("bob@example.fr")

    assert [u.username for u in by_username] == ["camille.bernard"]
    assert [u.username for u in by_display_name] == ["bob.martin"]
    assert [u.username for u in by_email] == ["bob.martin"]


async def test_search_returns_empty_when_no_match(db_session, make_user):
    await make_user()
    repo = UserRepository(db_session)

    assert await repo.search("nonexistent") == []


async def test_search_respects_limit(db_session, make_user):
    for i in range(5):
        await make_user(id=uuid.uuid4(), username=f"user{i}", email=f"user{i}@example.fr")
    repo = UserRepository(db_session)

    results = await repo.search("user", limit=2)

    assert len(results) == 2
