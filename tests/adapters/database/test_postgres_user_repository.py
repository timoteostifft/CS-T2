from uuid import uuid4

from recomendacoes_api.adapters.database.postgres_user_repository import PostgresUserRepository
from recomendacoes_api.domain.entities import User


def make_user(email: str = "ana@example.com") -> User:
    return User.create(name="Ana", email=email, password_hash="hash")


def test_save_then_find_by_id_returns_the_user(session_factory):
    repository = PostgresUserRepository(session_factory)
    user = make_user()

    repository.save(user)

    assert repository.find_by_id(user.id) == user


def test_find_by_id_returns_none_when_missing(session_factory):
    assert PostgresUserRepository(session_factory).find_by_id(uuid4()) is None


def test_find_by_email_returns_the_matching_user(session_factory):
    repository = PostgresUserRepository(session_factory)
    user = make_user()
    repository.save(user)
    repository.save(make_user("bia@example.com"))

    assert repository.find_by_email("ana@example.com") == user


def test_find_by_email_returns_none_when_missing(session_factory):
    assert PostgresUserRepository(session_factory).find_by_email("none@example.com") is None
