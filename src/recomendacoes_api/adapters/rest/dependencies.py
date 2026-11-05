from functools import lru_cache

from recomendacoes_api.adapters.database.postgres_city_repository import PostgresCityRepository
from recomendacoes_api.adapters.database.postgres_place_repository import PostgresPlaceRepository
from recomendacoes_api.adapters.database.postgres_review_repository import PostgresReviewRepository
from recomendacoes_api.adapters.database.postgres_state_repository import PostgresStateRepository
from recomendacoes_api.adapters.database.session import sessions
from recomendacoes_api.application.use_cases import (
    CreatePlaceUseCase,
    GetPlaceUseCase,
    ListCitiesUseCase,
    ListPlacesUseCase,
    ListReviewsUseCase,
    ListStatesUseCase,
    SubmitReviewUseCase,
)


@lru_cache
def get_place_repository() -> PostgresPlaceRepository:
    return PostgresPlaceRepository(sessions)


@lru_cache
def get_review_repository() -> PostgresReviewRepository:
    return PostgresReviewRepository(sessions)


@lru_cache
def get_state_repository() -> PostgresStateRepository:
    return PostgresStateRepository(sessions)


@lru_cache
def get_city_repository() -> PostgresCityRepository:
    return PostgresCityRepository(sessions)


def get_get_place_use_case() -> GetPlaceUseCase:
    return GetPlaceUseCase(get_place_repository())


def get_create_place_use_case() -> CreatePlaceUseCase:
    return CreatePlaceUseCase(get_place_repository(), get_city_repository())


def get_list_places_use_case() -> ListPlacesUseCase:
    return ListPlacesUseCase(get_place_repository())


def get_submit_review_use_case() -> SubmitReviewUseCase:
    return SubmitReviewUseCase(get_place_repository(), get_review_repository())


def get_list_reviews_use_case() -> ListReviewsUseCase:
    return ListReviewsUseCase(get_place_repository(), get_review_repository())


def get_list_states_use_case() -> ListStatesUseCase:
    return ListStatesUseCase(get_state_repository())


def get_list_cities_use_case() -> ListCitiesUseCase:
    return ListCitiesUseCase(get_city_repository())
