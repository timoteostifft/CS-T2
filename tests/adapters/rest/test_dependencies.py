from recomendacoes_api.adapters.rest import dependencies
from recomendacoes_api.application.use_cases import (
    CreateTripUseCase,
    DeleteTripUseCase,
    GetCurrentUserUseCase,
    GetTripUseCase,
    ListTripsUseCase,
    LoginUserUseCase,
    RegisterUserUseCase,
    UpdateTripUseCase,
)


def test_collaborators_are_cached_singletons():
    assert dependencies.get_user_repository() is dependencies.get_user_repository()
    assert dependencies.get_trip_repository() is dependencies.get_trip_repository()
    assert dependencies.get_password_hasher() is dependencies.get_password_hasher()
    assert dependencies.get_token_service() is dependencies.get_token_service()


def test_use_case_providers_build_the_expected_use_cases():
    assert isinstance(dependencies.get_register_user_use_case(), RegisterUserUseCase)
    assert isinstance(dependencies.get_login_user_use_case(), LoginUserUseCase)
    assert isinstance(dependencies.get_get_current_user_use_case(), GetCurrentUserUseCase)
    assert isinstance(dependencies.get_create_trip_use_case(), CreateTripUseCase)
    assert isinstance(dependencies.get_list_trips_use_case(), ListTripsUseCase)
    assert isinstance(dependencies.get_get_trip_use_case(), GetTripUseCase)
    assert isinstance(dependencies.get_update_trip_use_case(), UpdateTripUseCase)
    assert isinstance(dependencies.get_delete_trip_use_case(), DeleteTripUseCase)
