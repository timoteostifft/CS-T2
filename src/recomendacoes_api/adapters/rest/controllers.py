from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from recomendacoes_api.adapters.rest.dependencies import (
    get_create_place_use_case,
    get_list_cities_use_case,
    get_list_places_use_case,
    get_list_states_use_case,
)
from recomendacoes_api.adapters.rest.schemas import (
    CityListRequest,
    CityResponse,
    PageResponse,
    PaginationRequest,
    PlaceRequest,
    PlaceResponse,
    StateResponse,
)
from recomendacoes_api.application.use_cases import (
    CreatePlaceUseCase,
    ListCitiesUseCase,
    ListPlacesUseCase,
    ListStatesUseCase,
)

router = APIRouter(prefix="/places", tags=["places"])
states_router = APIRouter(prefix="/states", tags=["locations"])
cities_router = APIRouter(prefix="/cities", tags=["locations"])


@router.get("")
def list_places(
    pagination: Annotated[PaginationRequest, Query()],
    use_case: ListPlacesUseCase = Depends(get_list_places_use_case),
) -> PageResponse[PlaceResponse]:
    page = use_case.execute(limit=pagination.limit, offset=pagination.offset)

    return PageResponse[PlaceResponse].from_page(page, PlaceResponse.from_entity)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_place(
    request: PlaceRequest,
    use_case: CreatePlaceUseCase = Depends(get_create_place_use_case),
) -> PlaceResponse:
    place = use_case.execute(
        name=request.name,
        category=request.category,
        city_id=request.city_id,
        rating=request.rating,
        cost=request.cost,
    )

    return PlaceResponse.from_entity(place)


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
