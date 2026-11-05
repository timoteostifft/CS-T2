from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from recomendacoes_api.adapters.rest.dependencies import (
    get_add_destination_use_case,
    get_change_collaborator_role_use_case,
    get_create_activity_use_case,
    get_create_trip_use_case,
    get_current_user,
    get_delete_destination_use_case,
    get_delete_trip_use_case,
    get_get_activity_use_case,
    get_get_trip_use_case,
    get_join_trip_use_case,
    get_list_activities_use_case,
    get_list_collaborators_use_case,
    get_list_destinations_use_case,
    get_list_reviews_use_case,
    get_list_scheduled_activities_use_case,
    get_list_trips_use_case,
    get_login_user_use_case,
    get_register_user_use_case,
    get_remove_collaborator_use_case,
    get_remove_scheduled_activity_use_case,
    get_reorder_destinations_use_case,
    get_schedule_activity_use_case,
    get_set_trip_budget_use_case,
    get_submit_review_use_case,
    get_update_destination_use_case,
    get_update_scheduled_activity_use_case,
    get_update_trip_use_case,
)
from recomendacoes_api.adapters.rest.schemas import (
    ActivityRequest,
    ActivityResponse,
    BudgetRequest,
    CollaboratorResponse,
    CollaboratorRoleRequest,
    DestinationRequest,
    DestinationResponse,
    HealthResponse,
    JoinTripRequest,
    LoginRequest,
    PageResponse,
    PaginationRequest,
    RegisterRequest,
    ReorderDestinationsRequest,
    ReviewRequest,
    ReviewResponse,
    ScheduleActivityRequest,
    ScheduledActivityDetailsRequest,
    ScheduledActivityResponse,
    TokenResponse,
    TripRequest,
    TripResponse,
    UserResponse,
)
from recomendacoes_api.application.use_cases import (
    AddDestinationUseCase,
    ChangeCollaboratorRoleUseCase,
    CreateActivityUseCase,
    CreateTripUseCase,
    DeleteDestinationUseCase,
    DeleteTripUseCase,
    GetActivityUseCase,
    GetTripUseCase,
    JoinTripUseCase,
    ListActivitiesUseCase,
    ListCollaboratorsUseCase,
    ListDestinationsUseCase,
    ListReviewsUseCase,
    ListScheduledActivitiesUseCase,
    ListTripsUseCase,
    LoginUserUseCase,
    RegisterUserUseCase,
    RemoveCollaboratorUseCase,
    RemoveScheduledActivityUseCase,
    ReorderDestinationsUseCase,
    ScheduleActivityUseCase,
    SetTripBudgetUseCase,
    SubmitReviewUseCase,
    UpdateDestinationUseCase,
    UpdateScheduledActivityUseCase,
    UpdateTripUseCase,
)
from recomendacoes_api.domain.entities import User

auth_router = APIRouter(prefix="/auth", tags=["auth"])
trips_router = APIRouter(prefix="/trips", tags=["trips"])
destinations_router = APIRouter(prefix="/trips/{trip_id}/destinations", tags=["destinations"])
activities_router = APIRouter(prefix="/activities", tags=["activities"])
scheduled_activities_router = APIRouter(
    prefix="/trips/{trip_id}/destinations/{destination_id}/activities",
    tags=["scheduled-activities"],
)
collaborators_router = APIRouter(prefix="/trips/{trip_id}/collaborators", tags=["collaborators"])
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

    return TripResponse.from_entity(trip, user.id)


@trips_router.post("/join", status_code=status.HTTP_201_CREATED)
def join_trip(
    request: JoinTripRequest,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[JoinTripUseCase, Depends(get_join_trip_use_case)],
) -> TripResponse:
    trip = use_case.execute(user.id, request.code)

    return TripResponse.from_entity(trip, user.id)


@trips_router.get("")
def list_trips(
    pagination: Annotated[PaginationRequest, Query()],
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ListTripsUseCase, Depends(get_list_trips_use_case)],
) -> PageResponse[TripResponse]:
    page = use_case.execute(user.id, limit=pagination.limit, offset=pagination.offset)

    return PageResponse[TripResponse].from_page(
        page, lambda trip: TripResponse.from_entity(trip, user.id)
    )


@trips_router.get("/{trip_id}")
def get_trip(
    trip_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[GetTripUseCase, Depends(get_get_trip_use_case)],
) -> TripResponse:
    trip = use_case.execute(user.id, trip_id)

    return TripResponse.from_entity(trip, user.id)


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

    return TripResponse.from_entity(trip, user.id)


@trips_router.put("/{trip_id}/budget")
def set_trip_budget(
    trip_id: UUID,
    request: BudgetRequest,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[SetTripBudgetUseCase, Depends(get_set_trip_budget_use_case)],
) -> TripResponse:
    trip = use_case.execute(user.id, trip_id, request.amount)

    return TripResponse.from_entity(trip, user.id)


@trips_router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[DeleteTripUseCase, Depends(get_delete_trip_use_case)],
) -> Response:
    use_case.execute(user.id, trip_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@destinations_router.post("", status_code=status.HTTP_201_CREATED)
def add_destination(
    trip_id: UUID,
    request: DestinationRequest,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[AddDestinationUseCase, Depends(get_add_destination_use_case)],
) -> DestinationResponse:
    destination = use_case.execute(
        user_id=user.id,
        trip_id=trip_id,
        name=request.name,
        location=request.location,
        category=request.category,
        arrival_date=request.arrival_date,
        departure_date=request.departure_date,
        photo_url=request.photo_url,
        description=request.description,
    )

    return DestinationResponse.from_entity(destination)


@destinations_router.get("")
def list_destinations(
    trip_id: UUID,
    pagination: Annotated[PaginationRequest, Query()],
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ListDestinationsUseCase, Depends(get_list_destinations_use_case)],
) -> PageResponse[DestinationResponse]:
    page = use_case.execute(user.id, trip_id, limit=pagination.limit, offset=pagination.offset)

    return PageResponse[DestinationResponse].from_page(page, DestinationResponse.from_entity)


@destinations_router.put("/order", status_code=status.HTTP_204_NO_CONTENT)
def reorder_destinations(
    trip_id: UUID,
    request: ReorderDestinationsRequest,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ReorderDestinationsUseCase, Depends(get_reorder_destinations_use_case)],
) -> Response:
    use_case.execute(user.id, trip_id, request.destination_ids)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@destinations_router.put("/{destination_id}")
def update_destination(
    trip_id: UUID,
    destination_id: UUID,
    request: DestinationRequest,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[UpdateDestinationUseCase, Depends(get_update_destination_use_case)],
) -> DestinationResponse:
    destination = use_case.execute(
        user_id=user.id,
        trip_id=trip_id,
        destination_id=destination_id,
        name=request.name,
        location=request.location,
        category=request.category,
        arrival_date=request.arrival_date,
        departure_date=request.departure_date,
        photo_url=request.photo_url,
        description=request.description,
    )

    return DestinationResponse.from_entity(destination)


@destinations_router.delete("/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_destination(
    trip_id: UUID,
    destination_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[DeleteDestinationUseCase, Depends(get_delete_destination_use_case)],
) -> Response:
    use_case.execute(user.id, trip_id, destination_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@activities_router.post(
    "", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)]
)
def create_activity(
    request: ActivityRequest,
    use_case: Annotated[CreateActivityUseCase, Depends(get_create_activity_use_case)],
) -> ActivityResponse:
    activity = use_case.execute(
        name=request.name,
        category=request.category,
        location=request.location,
        description=request.description,
        photo_url=request.photo_url,
    )

    return ActivityResponse.from_entity(activity)


@activities_router.get("")
def list_activities(
    pagination: Annotated[PaginationRequest, Query()],
    use_case: Annotated[ListActivitiesUseCase, Depends(get_list_activities_use_case)],
) -> PageResponse[ActivityResponse]:
    page = use_case.execute(limit=pagination.limit, offset=pagination.offset)

    return PageResponse[ActivityResponse].from_page(page, ActivityResponse.from_entity)


@activities_router.get("/{activity_id}")
def get_activity(
    activity_id: UUID,
    use_case: Annotated[GetActivityUseCase, Depends(get_get_activity_use_case)],
) -> ActivityResponse:
    activity = use_case.execute(activity_id)

    return ActivityResponse.from_entity(activity)


@activities_router.get("/{activity_id}/reviews")
def list_reviews(
    activity_id: UUID,
    pagination: Annotated[PaginationRequest, Query()],
    use_case: Annotated[ListReviewsUseCase, Depends(get_list_reviews_use_case)],
) -> PageResponse[ReviewResponse]:
    page = use_case.execute(activity_id, limit=pagination.limit, offset=pagination.offset)

    return PageResponse[ReviewResponse].from_page(page, ReviewResponse.from_entity)


@activities_router.put("/{activity_id}/review")
def submit_review(
    activity_id: UUID,
    request: ReviewRequest,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[SubmitReviewUseCase, Depends(get_submit_review_use_case)],
) -> ReviewResponse:
    details = use_case.execute(user, activity_id, request.rating, request.comment)

    return ReviewResponse.from_entity(details)


@scheduled_activities_router.post("", status_code=status.HTTP_201_CREATED)
def schedule_activity(
    trip_id: UUID,
    destination_id: UUID,
    request: ScheduleActivityRequest,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ScheduleActivityUseCase, Depends(get_schedule_activity_use_case)],
) -> ScheduledActivityResponse:
    details = use_case.execute(
        user_id=user.id,
        trip_id=trip_id,
        destination_id=destination_id,
        activity_id=request.activity_id,
        starts_at=request.starts_at,
        duration_minutes=request.duration_minutes,
        planned_cost=request.planned_cost,
        status=request.status,
    )

    return ScheduledActivityResponse.from_entity(details)


@scheduled_activities_router.get("")
def list_scheduled_activities(
    trip_id: UUID,
    destination_id: UUID,
    pagination: Annotated[PaginationRequest, Query()],
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[
        ListScheduledActivitiesUseCase, Depends(get_list_scheduled_activities_use_case)
    ],
) -> PageResponse[ScheduledActivityResponse]:
    page = use_case.execute(
        user.id, trip_id, destination_id, limit=pagination.limit, offset=pagination.offset
    )

    return PageResponse[ScheduledActivityResponse].from_page(
        page, ScheduledActivityResponse.from_entity
    )


@scheduled_activities_router.put("/{scheduled_id}")
def update_scheduled_activity(
    trip_id: UUID,
    destination_id: UUID,
    scheduled_id: UUID,
    request: ScheduledActivityDetailsRequest,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[
        UpdateScheduledActivityUseCase, Depends(get_update_scheduled_activity_use_case)
    ],
) -> ScheduledActivityResponse:
    details = use_case.execute(
        user_id=user.id,
        trip_id=trip_id,
        destination_id=destination_id,
        scheduled_id=scheduled_id,
        starts_at=request.starts_at,
        duration_minutes=request.duration_minutes,
        planned_cost=request.planned_cost,
        status=request.status,
    )

    return ScheduledActivityResponse.from_entity(details)


@scheduled_activities_router.delete("/{scheduled_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_scheduled_activity(
    trip_id: UUID,
    destination_id: UUID,
    scheduled_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[
        RemoveScheduledActivityUseCase, Depends(get_remove_scheduled_activity_use_case)
    ],
) -> Response:
    use_case.execute(user.id, trip_id, destination_id, scheduled_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@collaborators_router.get("")
def list_collaborators(
    trip_id: UUID,
    pagination: Annotated[PaginationRequest, Query()],
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ListCollaboratorsUseCase, Depends(get_list_collaborators_use_case)],
) -> PageResponse[CollaboratorResponse]:
    page = use_case.execute(user.id, trip_id, limit=pagination.limit, offset=pagination.offset)

    return PageResponse[CollaboratorResponse].from_page(page, CollaboratorResponse.from_entity)


@collaborators_router.put("/{collaborator_user_id}")
def change_collaborator_role(
    trip_id: UUID,
    collaborator_user_id: UUID,
    request: CollaboratorRoleRequest,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[
        ChangeCollaboratorRoleUseCase, Depends(get_change_collaborator_role_use_case)
    ],
) -> CollaboratorResponse:
    details = use_case.execute(user.id, trip_id, collaborator_user_id, request.role)

    return CollaboratorResponse.from_entity(details)


@collaborators_router.delete("/{collaborator_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_collaborator(
    trip_id: UUID,
    collaborator_user_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[RemoveCollaboratorUseCase, Depends(get_remove_collaborator_use_case)],
) -> Response:
    use_case.execute(user.id, trip_id, collaborator_user_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@health_router.get("")
def health() -> HealthResponse:
    return HealthResponse()
