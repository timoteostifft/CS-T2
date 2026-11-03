from functools import lru_cache

from recomendacoes_api.adapters.database.postgres_city_repository import PostgresCityRepository
from recomendacoes_api.adapters.database.postgres_place_repository import PostgresPlaceRepository
from recomendacoes_api.adapters.database.postgres_state_repository import PostgresStateRepository
from recomendacoes_api.adapters.database.session import sessions
from recomendacoes_api.application.use_cases import (
    ListCitiesUseCase,
    ListPlacesUseCase,
    ListStatesUseCase,
)


@lru_cache
def get_place_repository() -> PostgresPlaceRepository:
    return PostgresPlaceRepository(sessions)


@lru_cache
def get_state_repository() -> PostgresStateRepository:
    return PostgresStateRepository(sessions)


@lru_cache
def get_city_repository() -> PostgresCityRepository:
    return PostgresCityRepository(sessions)


def get_list_places_use_case() -> ListPlacesUseCase:
    return ListPlacesUseCase(get_place_repository())


def get_list_states_use_case() -> ListStatesUseCase:
    return ListStatesUseCase(get_state_repository())


def get_list_cities_use_case() -> ListCitiesUseCase:
    return ListCitiesUseCase(get_city_repository())
