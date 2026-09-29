from uuid import UUID

from dynamic_ranker import DynamicRanker, DynamicRankerError, RankedItem
from recomendacoes_api.domain.entities import Place
from recomendacoes_api.domain.exceptions import (
    InvalidRankWeightsError,
    PlaceNotFoundError,
)
from recomendacoes_api.ports.repositories import PlaceRepository


class ListPlacesUseCase:
    def __init__(self, place_repository: PlaceRepository) -> None:
        self._place_repository = place_repository

    def execute(self, limit: int = 10, offset: int = 0) -> tuple[int, list[Place]]:
        return self._place_repository.list_paginated(limit, offset)


class CreatePlaceUseCase:
    def __init__(self, place_repository: PlaceRepository) -> None:
        self._place_repository = place_repository

    def execute(
        self,
        name: str,
        category: str,
        rating: float,
        cost: float,
        popularity: float,
    ) -> Place:
        place = Place.create(
            name=name,
            category=category,
            rating=rating,
            cost=cost,
            popularity=popularity,
        )
        return self._place_repository.save(place)


class GetPlaceByIdUseCase:
    def __init__(self, place_repository: PlaceRepository) -> None:
        self._place_repository = place_repository

    def execute(self, id: UUID) -> Place:
        place = self._place_repository.find_by_id(id)
        if not place:
            raise PlaceNotFoundError(f"Place with id {id} not found")
        return place


class UpdatePlaceUseCase:
    def __init__(self, place_repository: PlaceRepository) -> None:
        self._place_repository = place_repository

    def execute(
        self,
        id: UUID,
        name: str | None = None,
        category: str | None = None,
        rating: float | None = None,
        cost: float | None = None,
        popularity: float | None = None,
    ) -> Place:
        place = self._place_repository.find_by_id(id)
        if not place:
            raise PlaceNotFoundError(f"Place with id {id} not found")

        updated_name = name if name is not None else place.name
        updated_category = category if category is not None else place.category
        updated_rating = rating if rating is not None else place.rating
        updated_cost = cost if cost is not None else place.cost
        updated_popularity = popularity if popularity is not None else place.popularity

        updated_place = Place(
            id=place.id,
            name=updated_name,
            category=updated_category,
            rating=updated_rating,
            cost=updated_cost,
            popularity=updated_popularity,
        )
        return self._place_repository.update(updated_place)


class DeletePlaceUseCase:
    def __init__(self, place_repository: PlaceRepository) -> None:
        self._place_repository = place_repository

    def execute(self, id: UUID) -> None:
        deleted = self._place_repository.delete(id)
        if not deleted:
            raise PlaceNotFoundError(f"Place with id {id} not found")


class RankPlacesUseCase:
    def __init__(self, place_repository: PlaceRepository) -> None:
        self._place_repository = place_repository

    def execute(self, weights: dict[str, float], limit: int = 5) -> list[RankedItem[Place]]:
        places = self._place_repository.list_all()
        try:
            return DynamicRanker.rank(places, weights, limit=limit)
        except DynamicRankerError as exc:
            raise InvalidRankWeightsError(str(exc)) from exc
