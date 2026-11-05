from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from recomendacoes_api.adapters.rest.dependencies import (
    get_create_trip_use_case,
    get_current_user,
    get_delete_trip_use_case,
    get_get_trip_use_case,
    get_list_trips_use_case,
    get_login_user_use_case,
    get_register_user_use_case,
    get_update_trip_use_case,
)
from recomendacoes_api.adapters.rest.schemas import (
    HealthResponse,
    LoginRequest,
    PageResponse,
    PaginationRequest,
    RegisterRequest,
    TokenResponse,
    TripRequest,
    TripResponse,
    UserResponse,
)
from recomendacoes_api.application.use_cases import (
    CreateTripUseCase,
    DeleteTripUseCase,
    GetTripUseCase,
    ListTripsUseCase,
    LoginUserUseCase,
    RegisterUserUseCase,
    UpdateTripUseCase,
)
from recomendacoes_api.domain.entities import User

auth_router = APIRouter(prefix="/auth", tags=["auth"])
trips_router = APIRouter(prefix="/trips", tags=["trips"])
health_router = APIRouter(prefix="/health", tags=["health"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_user_use_case)],
) -> UserResponse:
    user = use_case.execute(name=request.name, email=request.email, password=request.password)

    return UserResponse.from_entity(user)


@auth_router.post("/login")
def login(
    request: LoginRequest,
    use_case: Annotated[LoginUserUseCase, Depends(get_login_user_use_case)],
) -> TokenResponse:
    token = use_case.execute(email=request.email, password=request.password)

    return TokenResponse.from_token(token)


@auth_router.get("/me")
def me(user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return UserResponse.from_entity(user)


@trips_router.post("", status_code=status.HTTP_201_CREATED)
def create_trip(
    request: TripRequest,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[CreateTripUseCase, Depends(get_create_trip_use_case)],
) -> TripResponse:
    trip = use_case.execute(
        user_id=user.id,
        name=request.name,
        description=request.description,
        start_date=request.start_date,
        end_date=request.end_date,
    )

    return TripResponse.from_entity(trip)


@trips_router.get("")
def list_trips(
    pagination: Annotated[PaginationRequest, Query()],
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ListTripsUseCase, Depends(get_list_trips_use_case)],
) -> PageResponse[TripResponse]:
    page = use_case.execute(user.id, limit=pagination.limit, offset=pagination.offset)

    return PageResponse[TripResponse].from_page(page, TripResponse.from_entity)


@trips_router.get("/{trip_id}")
def get_trip(
    trip_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[GetTripUseCase, Depends(get_get_trip_use_case)],
) -> TripResponse:
    trip = use_case.execute(user.id, trip_id)

    return TripResponse.from_entity(trip)


@trips_router.put("/{trip_id}")
def update_trip(
    trip_id: UUID,
    request: TripRequest,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[UpdateTripUseCase, Depends(get_update_trip_use_case)],
) -> TripResponse:
    trip = use_case.execute(
        user_id=user.id,
        trip_id=trip_id,
        name=request.name,
        description=request.description,
        start_date=request.start_date,
        end_date=request.end_date,
    )

    return TripResponse.from_entity(trip)


@trips_router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[DeleteTripUseCase, Depends(get_delete_trip_use_case)],
) -> Response:
    use_case.execute(user.id, trip_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@health_router.get("")
def health() -> HealthResponse:
    return HealthResponse()
