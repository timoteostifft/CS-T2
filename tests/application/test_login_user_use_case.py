import pytest

from recomendacoes_api.application.use_cases import LoginUserUseCase
from recomendacoes_api.domain.entities import User
from recomendacoes_api.domain.exceptions import InvalidCredentialsError
from tests.adapters.database.mock_user_repository import MockUserRepository
from tests.adapters.security.mock_password_hasher import MockPasswordHasher
from tests.adapters.security.mock_token_service import MockTokenService


def build_use_case() -> tuple[LoginUserUseCase, User]:
    user = User.create(name="Ana", email="ana@example.com", password_hash="hashed:secret123")
    use_case = LoginUserUseCase(
        MockUserRepository([user]), MockPasswordHasher(), MockTokenService()
    )

    return use_case, user


def test_execute_returns_a_token_for_valid_credentials():
    use_case, user = build_use_case()

    token = use_case.execute(email="Ana@Example.com", password="secret123")

    assert token == MockTokenService().issue(user.id)


def test_execute_rejects_a_wrong_password():
    use_case, _ = build_use_case()

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(email="ana@example.com", password="wrong-pass")


def test_execute_rejects_an_unknown_email():
    use_case, _ = build_use_case()

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(email="none@example.com", password="secret123")
