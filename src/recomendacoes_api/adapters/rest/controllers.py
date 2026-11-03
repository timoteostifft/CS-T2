from fastapi import APIRouter, Depends

from recomendacoes_api.adapters.rest.dependencies import (
    get_list_cities_use_case,
    get_list_places_use_case,
    get_list_states_use_case,
)
from recomendacoes_api.adapters.rest.schemas import CityResponse, PlaceResponse, StateResponse
from recomendacoes_api.application.use_cases import (
    ListCitiesUseCase,
    ListPlacesUseCase,
    ListStatesUseCase,
)

router = APIRouter(prefix="/places", tags=["places"])
states_router = APIRouter(prefix="/states", tags=["locations"])
cities_router = APIRouter(prefix="/cities", tags=["locations"])


@router.get("", response_model=list[PlaceResponse])
def list_places(
    use_case: ListPlacesUseCase = Depends(get_list_places_use_case),
) -> list[PlaceResponse]:
    places = use_case.execute()
    return [PlaceResponse.from_entity(place) for place in places]


@states_router.get("", response_model=list[StateResponse])
def list_states(
    use_case: ListStatesUseCase = Depends(get_list_states_use_case),
) -> list[StateResponse]:
    return [StateResponse.from_entity(state) for state in use_case.execute()]


@cities_router.get("", response_model=list[CityResponse])
def list_cities(
    state_code: str | None = None,
    use_case: ListCitiesUseCase = Depends(get_list_cities_use_case),
) -> list[CityResponse]:
    return [CityResponse.from_entity(city) for city in use_case.execute(state_code)]
