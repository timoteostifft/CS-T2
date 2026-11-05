from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status

from recomendacoes_api.adapters.rest.dependencies import (
    get_create_place_use_case,
    get_get_place_use_case,
    get_list_cities_use_case,
    get_list_places_use_case,
    get_list_reviews_use_case,
    get_list_states_use_case,
    get_report_place_use_case,
    get_submit_review_use_case,
)
from recomendacoes_api.adapters.rest.schemas import (
    CityListRequest,
    CityResponse,
    HealthResponse,
    PageResponse,
    PaginationRequest,
    PlaceListRequest,
    PlaceRequest,
    PlaceResponse,
    ReportResponse,
    ReviewRequest,
    ReviewResponse,
    StateResponse,
)
from recomendacoes_api.application.use_cases import (
    CreatePlaceUseCase,
    GetPlaceUseCase,
    ListCitiesUseCase,
    ListPlacesUseCase,
    ListReviewsUseCase,
    ListStatesUseCase,
    ReportPlaceUseCase,
    SubmitReviewUseCase,
)

router = APIRouter(prefix="/places", tags=["places"])
states_router = APIRouter(prefix="/states", tags=["locations"])
cities_router = APIRouter(prefix="/cities", tags=["locations"])
health_router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def list_places(
    filters: Annotated[PlaceListRequest, Query()],
    use_case: ListPlacesUseCase = Depends(get_list_places_use_case),
) -> PageResponse[PlaceResponse]:
    page = use_case.execute(
        category=filters.category,
        city_id=filters.city_id,
        min_rating=filters.min_rating,
        max_cost=filters.max_cost,
        sort=filters.sort,
        limit=filters.limit,
        offset=filters.offset,
    )

    return PageResponse[PlaceResponse].from_page(page, PlaceResponse.from_entity)


@router.get("/{place_id}")
def get_place(
    place_id: UUID,
    use_case: GetPlaceUseCase = Depends(get_get_place_use_case),
) -> PlaceResponse:
    place = use_case.execute(place_id)

    return PlaceResponse.from_entity(place)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_place(
    request: PlaceRequest,
    use_case: CreatePlaceUseCase = Depends(get_create_place_use_case),
) -> PlaceResponse:
    place = use_case.execute(
        name=request.name,
        category=request.category,
        city_id=request.city_id,
        cost=request.cost,
    )

    return PlaceResponse.from_entity(place)


@router.get("/{place_id}/reviews")
def list_reviews(
    place_id: UUID,
    pagination: Annotated[PaginationRequest, Query()],
    use_case: ListReviewsUseCase = Depends(get_list_reviews_use_case),
) -> PageResponse[ReviewResponse]:
    page = use_case.execute(place_id, limit=pagination.limit, offset=pagination.offset)

    return PageResponse[ReviewResponse].from_page(page, ReviewResponse.from_entity)


@router.post("/{place_id}/reviews", status_code=status.HTTP_201_CREATED)
def submit_review(
    place_id: UUID,
    request: ReviewRequest,
    use_case: Annotated[SubmitReviewUseCase, Depends(get_submit_review_use_case)],
) -> ReviewResponse:
    review = use_case.execute(
        place_id=place_id,
        device_id=request.device_id,
        rating=request.rating,
        comment=request.comment,
    )

    return ReviewResponse.from_entity(review)


@router.post("/{place_id}/reports", status_code=status.HTTP_201_CREATED)
def report_place(
    place_id: UUID,
    request: Request,
    use_case: Annotated[ReportPlaceUseCase, Depends(get_report_place_use_case)],
    user_agent: Annotated[str, Header()] = "",
) -> ReportResponse:
    ip_address = request.client.host if request.client else ""
    report = use_case.execute(place_id=place_id, ip_address=ip_address, user_agent=user_agent)

    return ReportResponse.from_entity(report)


@states_router.get("")
def list_states(
    pagination: Annotated[PaginationRequest, Query()],
    use_case: ListStatesUseCase = Depends(get_list_states_use_case),
) -> PageResponse[StateResponse]:
    page = use_case.execute(limit=pagination.limit, offset=pagination.offset)

    return PageResponse[StateResponse].from_page(page, StateResponse.from_entity)


@cities_router.get("")
def list_cities(
    filters: Annotated[CityListRequest, Query()],
    use_case: ListCitiesUseCase = Depends(get_list_cities_use_case),
) -> PageResponse[CityResponse]:
    page = use_case.execute(
        state_code=filters.state_code, limit=filters.limit, offset=filters.offset
    )

    return PageResponse[CityResponse].from_page(page, CityResponse.from_entity)


@health_router.get("")
def health() -> HealthResponse:
    return HealthResponse()
