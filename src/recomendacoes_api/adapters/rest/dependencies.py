from functools import lru_cache

from recomendacoes_api.adapters.database.postgres_place_repository import PostgresPlaceRepository
from recomendacoes_api.adapters.database.session import SessionLocal
from recomendacoes_api.application.use_cases import ListPlacesUseCase


@lru_cache
def get_place_repository() -> PostgresPlaceRepository:
    return PostgresPlaceRepository(SessionLocal)


def get_list_places_use_case() -> ListPlacesUseCase:
    return ListPlacesUseCase(get_place_repository())
