import pytest

from recomendacoes_api.application.use_cases import RegisterUserUseCase
from recomendacoes_api.domain.entities import User
from recomendacoes_api.domain.exceptions import EmailAlreadyRegisteredError, InvalidUserError
from tests.adapters.database.mock_user_repository import MockUserRepository
from tests.adapters.security.mock_password_hasher import MockPasswordHasher


def test_execute_saves_the_user_with_a_hashed_password():
    repository = MockUserRepository()
    use_case = RegisterUserUseCase(repository, MockPasswordHasher())

    user = use_case.execute(name="Ana", email="Ana@Example.com", password="secret123")

    assert repository.users == [user]
    assert user.email == "ana@example.com"
    assert user.password_hash == "hashed:secret123"


def test_execute_rejects_a_short_password():
    repository = MockUserRepository()
    use_case = RegisterUserUseCase(repository, MockPasswordHasher())

    with pytest.raises(InvalidUserError):
        use_case.execute(name="Ana", email="ana@example.com", password="short")

    assert repository.users == []


def test_execute_rejects_an_email_already_registered():
    existing = User.create(name="Ana", email="ana@example.com", password_hash="hash")
    repository = MockUserRepository([existing])
    use_case = RegisterUserUseCase(repository, MockPasswordHasher())

    with pytest.raises(EmailAlreadyRegisteredError):
        use_case.execute(name="Other", email="ANA@example.com", password="secret123")

    assert repository.users == [existing]


def test_execute_rejects_an_invalid_user():
    repository = MockUserRepository()
    use_case = RegisterUserUseCase(repository, MockPasswordHasher())

    with pytest.raises(InvalidUserError):
        use_case.execute(name=" ", email="ana@example.com", password="secret123")

    assert repository.users == []
