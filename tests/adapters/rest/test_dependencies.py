from recomendacoes_api.adapters.rest import dependencies
from recomendacoes_api.application.use_cases import (
    CreatePlaceUseCase,
    ListCitiesUseCase,
    ListPlacesUseCase,
    ListStatesUseCase,
)


def test_repositories_are_cached_singletons():
    assert dependencies.get_place_repository() is dependencies.get_place_repository()
    assert dependencies.get_state_repository() is dependencies.get_state_repository()
    assert dependencies.get_city_repository() is dependencies.get_city_repository()


def test_use_case_providers_build_the_expected_use_cases():
    assert isinstance(dependencies.get_list_places_use_case(), ListPlacesUseCase)
    assert isinstance(dependencies.get_create_place_use_case(), CreatePlaceUseCase)
    assert isinstance(dependencies.get_list_states_use_case(), ListStatesUseCase)
    assert isinstance(dependencies.get_list_cities_use_case(), ListCitiesUseCase)
