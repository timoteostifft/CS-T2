from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from recomendacoes_api.adapters.rest.dependencies import (
    get_create_place_use_case,
    get_delete_place_use_case,
    get_get_place_by_id_use_case,
    get_list_places_use_case,
    get_rank_places_use_case,
    get_update_place_use_case,
    verify_bearer_token,
)
from recomendacoes_api.adapters.rest.schemas import (
    PaginatedPlacesResponse,
    PlaceCreate,
    PlaceRanked,
    PlaceResponse,
    PlaceUpdate,
    RankWeightsPayload,
)
from recomendacoes_api.application.use_cases import (
    CreatePlaceUseCase,
    DeletePlaceUseCase,
    GetPlaceByIdUseCase,
    ListPlacesUseCase,
    RankPlacesUseCase,
    UpdatePlaceUseCase,
)

router = APIRouter(prefix="/places", tags=["Places"])


@router.get(
    "",
    response_model=PaginatedPlacesResponse,
    dependencies=[Depends(verify_bearer_token)],
    summary="Listar todos os locais",
)
def list_places(
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    use_case: ListPlacesUseCase = Depends(get_list_places_use_case),
) -> PaginatedPlacesResponse:
    total, places = use_case.execute(limit=limit, offset=offset)
    return PaginatedPlacesResponse(
        total=total,
        items=[PlaceResponse.from_entity(p) for p in places],
    )


@router.post(
    "",
    response_model=PlaceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_bearer_token)],
    summary="Criar um novo local",
)
def create_place(
    request: PlaceCreate,
    use_case: CreatePlaceUseCase = Depends(get_create_place_use_case),
) -> PlaceResponse:
    place = use_case.execute(
        name=request.name,
        category=request.category,
        rating=request.rating,
        cost=request.cost,
        popularity=request.popularity,
    )
    return PlaceResponse.from_entity(place)


@router.post(
    "/rank",
    response_model=list[PlaceRanked],
    dependencies=[Depends(verify_bearer_token)],
    tags=["Motor de Recomendações"],
    summary="Ranqueamento dinâmico de locais",
)
def rank_places(
    payload: RankWeightsPayload,
    limit: int = Query(default=5),
    use_case: RankPlacesUseCase = Depends(get_rank_places_use_case),
) -> list[PlaceRanked]:
    ranked_items = use_case.execute(weights=payload.weights, limit=limit)
    return [PlaceRanked.from_ranked_item(r) for r in ranked_items]


@router.get(
    "/{id}",
    response_model=PlaceResponse,
    dependencies=[Depends(verify_bearer_token)],
    summary="Obter detalhes de um local",
)
def get_place_by_id(
    id: UUID,
    use_case: GetPlaceByIdUseCase = Depends(get_get_place_by_id_use_case),
) -> PlaceResponse:
    place = use_case.execute(id)
    return PlaceResponse.from_entity(place)


@router.put(
    "/{id}",
    response_model=PlaceResponse,
    dependencies=[Depends(verify_bearer_token)],
    summary="Atualizar um local",
)
def update_place(
    id: UUID,
    request: PlaceUpdate,
    use_case: UpdatePlaceUseCase = Depends(get_update_place_use_case),
) -> PlaceResponse:
    place = use_case.execute(
        id=id,
        name=request.name,
        category=request.category,
        rating=request.rating,
        cost=request.cost,
        popularity=request.popularity,
    )
    return PlaceResponse.from_entity(place)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_bearer_token)],
    summary="Eliminar um local",
)
def delete_place(
    id: UUID,
    use_case: DeletePlaceUseCase = Depends(get_delete_place_use_case),
) -> None:
    use_case.execute(id)
