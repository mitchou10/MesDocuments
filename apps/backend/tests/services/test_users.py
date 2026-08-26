import uuid

from app.repositories.users import UserRepository
from app.services.users import UserService


async def test_search_users_below_min_length_returns_empty_without_querying(db_session, make_user):
    await make_user()
    service = UserService(UserRepository(db_session))

    assert await service.search_users("c") == []
    assert await service.search_users(" ") == []


async def test_search_users_delegates_to_repository(db_session, make_user):
    await make_user(id=uuid.uuid4(), username="camille.bernard", email="camille@example.fr")
    service = UserService(UserRepository(db_session))

    results = await service.search_users("camille")

    assert [u.username for u in results] == ["camille.bernard"]


async def test_get_user_returns_existing_user(db_session, make_user):
    user = await make_user()
    service = UserService(UserRepository(db_session))

    found = await service.get_user(user.id)

    assert found is not None
    assert found.id == user.id


async def test_get_user_returns_none_when_missing(db_session):
    service = UserService(UserRepository(db_session))

    assert await service.get_user(uuid.uuid4()) is None
