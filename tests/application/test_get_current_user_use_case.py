from uuid import uuid4

import pytest

from recomendacoes_api.application.use_cases import GetCurrentUserUseCase
from recomendacoes_api.domain.entities import User
from recomendacoes_api.domain.exceptions import InvalidTokenError
from tests.adapters.database.mock_user_repository import MockUserRepository
from tests.adapters.security.mock_token_service import MockTokenService


def build_use_case() -> tuple[GetCurrentUserUseCase, User]:
    user = User.create(name="Ana", email="ana@example.com", password_hash="hash")

    return GetCurrentUserUseCase(MockUserRepository([user]), MockTokenService()), user


def test_execute_returns_the_user_owning_the_token():
    use_case, user = build_use_case()

    assert use_case.execute(MockTokenService().issue(user.id)) == user


def test_execute_rejects_a_missing_token():
    use_case, _ = build_use_case()

    with pytest.raises(InvalidTokenError):
        use_case.execute(None)


def test_execute_rejects_an_invalid_token():
    use_case, _ = build_use_case()

    with pytest.raises(InvalidTokenError):
        use_case.execute("garbage")


def test_execute_rejects_a_token_of_an_unknown_user():
    use_case, _ = build_use_case()

    with pytest.raises(InvalidTokenError):
        use_case.execute(MockTokenService().issue(uuid4()))
