from functools import lru_cache
from typing import Any

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from recomendacoes_api.adapters.database.postgres_place_repository import PostgresPlaceRepository
from recomendacoes_api.adapters.database.session import SessionLocal
from recomendacoes_api.adapters.rest.exception_handlers import UnauthorizedError
from recomendacoes_api.application.use_cases import (
    CreatePlaceUseCase,
    DeletePlaceUseCase,
    GetPlaceByIdUseCase,
    ListPlacesUseCase,
    RankPlacesUseCase,
    UpdatePlaceUseCase,
)
from recomendacoes_api.settings import settings

security = HTTPBearer(auto_error=False)


def create_access_token(data: dict[str, Any]) -> str:
    return jwt.encode(data, settings.jwt_secret, algorithm="HS256")


def verify_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any]:
    if credentials is None or not credentials.credentials:
        raise UnauthorizedError("Token JWT ausente, inválido ou expirado.")

    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Token JWT ausente, inválido ou expirado.") from exc


@lru_cache
def get_place_repository() -> PostgresPlaceRepository:
    return PostgresPlaceRepository(SessionLocal)


def get_list_places_use_case() -> ListPlacesUseCase:
    return ListPlacesUseCase(get_place_repository())


def get_create_place_use_case() -> CreatePlaceUseCase:
    return CreatePlaceUseCase(get_place_repository())


def get_get_place_by_id_use_case() -> GetPlaceByIdUseCase:
    return GetPlaceByIdUseCase(get_place_repository())


def get_update_place_use_case() -> UpdatePlaceUseCase:
    return UpdatePlaceUseCase(get_place_repository())


def get_delete_place_use_case() -> DeletePlaceUseCase:
    return DeletePlaceUseCase(get_place_repository())


def get_rank_places_use_case() -> RankPlacesUseCase:
    return RankPlacesUseCase(get_place_repository())
