from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from recomendacoes_api.adapters.database.postgres_trip_repository import PostgresTripRepository
from recomendacoes_api.adapters.database.postgres_user_repository import PostgresUserRepository
from recomendacoes_api.adapters.database.session import sessions
from recomendacoes_api.adapters.security.argon2_password_hasher import Argon2PasswordHasher
from recomendacoes_api.adapters.security.jwt_token_service import JwtTokenService
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
from recomendacoes_api.domain.entities import User
from recomendacoes_api.settings import settings

bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache
def get_user_repository() -> PostgresUserRepository:
    return PostgresUserRepository(sessions)


@lru_cache
def get_trip_repository() -> PostgresTripRepository:
    return PostgresTripRepository(sessions)


@lru_cache
def get_password_hasher() -> Argon2PasswordHasher:
    return Argon2PasswordHasher()


@lru_cache
def get_token_service() -> JwtTokenService:
    return JwtTokenService(settings.jwt_secret, settings.jwt_expire_minutes)


def get_register_user_use_case() -> RegisterUserUseCase:
    return RegisterUserUseCase(get_user_repository(), get_password_hasher())


def get_login_user_use_case() -> LoginUserUseCase:
    return LoginUserUseCase(get_user_repository(), get_password_hasher(), get_token_service())


def get_get_current_user_use_case() -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(get_user_repository(), get_token_service())


def get_create_trip_use_case() -> CreateTripUseCase:
    return CreateTripUseCase(get_trip_repository())


def get_list_trips_use_case() -> ListTripsUseCase:
    return ListTripsUseCase(get_trip_repository())


def get_get_trip_use_case() -> GetTripUseCase:
    return GetTripUseCase(get_trip_repository())


def get_update_trip_use_case() -> UpdateTripUseCase:
    return UpdateTripUseCase(get_trip_repository())


def get_delete_trip_use_case() -> DeleteTripUseCase:
    return DeleteTripUseCase(get_trip_repository())


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    use_case: Annotated[GetCurrentUserUseCase, Depends(get_get_current_user_use_case)],
) -> User:
    token = credentials.credentials if credentials else None

    return use_case.execute(token)
