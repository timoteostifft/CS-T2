from fastapi import APIRouter, Depends

from recomendacoes_api.adapters.rest.dependencies import get_list_places_use_case
from recomendacoes_api.adapters.rest.schemas import PlaceResponse
from recomendacoes_api.application.use_cases import ListPlacesUseCase

router = APIRouter(prefix="/places", tags=["places"])


@router.get("", response_model=list[PlaceResponse])
def list_places(
    use_case: ListPlacesUseCase = Depends(get_list_places_use_case),
) -> list[PlaceResponse]:
    places = use_case.execute()
    return [PlaceResponse.from_entity(place) for place in places]
