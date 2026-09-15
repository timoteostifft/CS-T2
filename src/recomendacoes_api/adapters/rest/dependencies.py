from functools import lru_cache

from recomendacoes_api.adapters.database.in_memory import InMemoryPlaceRepository
from recomendacoes_api.application.use_cases import ListPlacesUseCase


@lru_cache
def get_place_repository() -> InMemoryPlaceRepository:
    return InMemoryPlaceRepository()


def get_list_places_use_case() -> ListPlacesUseCase:
    return ListPlacesUseCase(get_place_repository())
