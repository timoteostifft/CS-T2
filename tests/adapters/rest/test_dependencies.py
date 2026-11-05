from recomendacoes_api.adapters.rest import dependencies
from recomendacoes_api.application.use_cases import (
    GetCurrentUserUseCase,
    LoginUserUseCase,
    RegisterUserUseCase,
)


def test_collaborators_are_cached_singletons():
    assert dependencies.get_user_repository() is dependencies.get_user_repository()
    assert dependencies.get_password_hasher() is dependencies.get_password_hasher()
    assert dependencies.get_token_service() is dependencies.get_token_service()


def test_use_case_providers_build_the_expected_use_cases():
    assert isinstance(dependencies.get_register_user_use_case(), RegisterUserUseCase)
    assert isinstance(dependencies.get_login_user_use_case(), LoginUserUseCase)
    assert isinstance(dependencies.get_get_current_user_use_case(), GetCurrentUserUseCase)
