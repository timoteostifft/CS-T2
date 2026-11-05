from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from recomendacoes_api.adapters.database.postgres_activity_repository import (
    PostgresActivityRepository,
)
from recomendacoes_api.adapters.database.postgres_destination_repository import (
    PostgresDestinationRepository,
)
from recomendacoes_api.adapters.database.postgres_scheduled_activity_repository import (
    PostgresScheduledActivityRepository,
)
from recomendacoes_api.adapters.database.postgres_trip_repository import PostgresTripRepository
from recomendacoes_api.adapters.database.postgres_user_repository import PostgresUserRepository
from recomendacoes_api.adapters.database.session import sessions
from recomendacoes_api.adapters.security.argon2_password_hasher import Argon2PasswordHasher
from recomendacoes_api.adapters.security.jwt_token_service import JwtTokenService
from recomendacoes_api.application.use_cases import (
    AddDestinationUseCase,
    ChangeCollaboratorRoleUseCase,
    CreateActivityUseCase,
    CreateTripUseCase,
    DeleteDestinationUseCase,
    DeleteTripUseCase,
    GetActivityUseCase,
    GetCurrentUserUseCase,
    GetTripUseCase,
    JoinTripUseCase,
    ListActivitiesUseCase,
    ListCollaboratorsUseCase,
    ListDestinationsUseCase,
    ListScheduledActivitiesUseCase,
    ListTripsUseCase,
    LoginUserUseCase,
    RegisterUserUseCase,
    RemoveCollaboratorUseCase,
    RemoveScheduledActivityUseCase,
    ReorderDestinationsUseCase,
    ScheduleActivityUseCase,
    SetTripBudgetUseCase,
    UpdateDestinationUseCase,
    UpdateScheduledActivityUseCase,
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
def get_destination_repository() -> PostgresDestinationRepository:
    return PostgresDestinationRepository(sessions)


@lru_cache
def get_activity_repository() -> PostgresActivityRepository:
    return PostgresActivityRepository(sessions)


@lru_cache
def get_scheduled_activity_repository() -> PostgresScheduledActivityRepository:
    return PostgresScheduledActivityRepository(sessions)


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


def get_set_trip_budget_use_case() -> SetTripBudgetUseCase:
    return SetTripBudgetUseCase(get_trip_repository())


def get_update_trip_use_case() -> UpdateTripUseCase:
    return UpdateTripUseCase(get_trip_repository())


def get_delete_trip_use_case() -> DeleteTripUseCase:
    return DeleteTripUseCase(get_trip_repository())


def get_add_destination_use_case() -> AddDestinationUseCase:
    return AddDestinationUseCase(get_trip_repository(), get_destination_repository())


def get_list_destinations_use_case() -> ListDestinationsUseCase:
    return ListDestinationsUseCase(get_trip_repository(), get_destination_repository())


def get_update_destination_use_case() -> UpdateDestinationUseCase:
    return UpdateDestinationUseCase(get_trip_repository(), get_destination_repository())


def get_delete_destination_use_case() -> DeleteDestinationUseCase:
    return DeleteDestinationUseCase(get_trip_repository(), get_destination_repository())


def get_reorder_destinations_use_case() -> ReorderDestinationsUseCase:
    return ReorderDestinationsUseCase(get_trip_repository(), get_destination_repository())


def get_create_activity_use_case() -> CreateActivityUseCase:
    return CreateActivityUseCase(get_activity_repository())


def get_list_activities_use_case() -> ListActivitiesUseCase:
    return ListActivitiesUseCase(get_activity_repository())


def get_get_activity_use_case() -> GetActivityUseCase:
    return GetActivityUseCase(get_activity_repository())


def get_schedule_activity_use_case() -> ScheduleActivityUseCase:
    return ScheduleActivityUseCase(
        get_trip_repository(),
        get_destination_repository(),
        get_activity_repository(),
        get_scheduled_activity_repository(),
    )


def get_list_scheduled_activities_use_case() -> ListScheduledActivitiesUseCase:
    return ListScheduledActivitiesUseCase(
        get_trip_repository(),
        get_destination_repository(),
        get_activity_repository(),
        get_scheduled_activity_repository(),
    )


def get_update_scheduled_activity_use_case() -> UpdateScheduledActivityUseCase:
    return UpdateScheduledActivityUseCase(
        get_trip_repository(),
        get_destination_repository(),
        get_activity_repository(),
        get_scheduled_activity_repository(),
    )


def get_remove_scheduled_activity_use_case() -> RemoveScheduledActivityUseCase:
    return RemoveScheduledActivityUseCase(
        get_trip_repository(),
        get_destination_repository(),
        get_scheduled_activity_repository(),
    )


def get_join_trip_use_case() -> JoinTripUseCase:
    return JoinTripUseCase(get_trip_repository())


def get_list_collaborators_use_case() -> ListCollaboratorsUseCase:
    return ListCollaboratorsUseCase(get_trip_repository(), get_user_repository())


def get_change_collaborator_role_use_case() -> ChangeCollaboratorRoleUseCase:
    return ChangeCollaboratorRoleUseCase(get_trip_repository(), get_user_repository())


def get_remove_collaborator_use_case() -> RemoveCollaboratorUseCase:
    return RemoveCollaboratorUseCase(get_trip_repository())


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    use_case: Annotated[GetCurrentUserUseCase, Depends(get_get_current_user_use_case)],
) -> User:
    token = credentials.credentials if credentials else None

    return use_case.execute(token)
