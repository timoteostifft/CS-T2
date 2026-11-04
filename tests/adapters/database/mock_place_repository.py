from uuid import UUID

from recomendacoes_api.domain.entities import Place


class MockPlaceRepository:
    def __init__(self, places: list[Place] | None = None) -> None:
        self._places = list(places or [])

    def list_all(
        self,
        category: str | None = None,
        city_id: int | None = None,
        min_rating: float | None = None,
        max_cost: float | None = None,
        sort: str = "name",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Place]:
        filtered = self._filter(category, city_id, min_rating, max_cost)
        ordered = self._sort(filtered, sort)
        end = None if limit is None else offset + limit

        return ordered[offset:end]

    def count_all(
        self,
        category: str | None = None,
        city_id: int | None = None,
        min_rating: float | None = None,
        max_cost: float | None = None,
    ) -> int:
        return len(self._filter(category, city_id, min_rating, max_cost))

    def find_by_id(self, place_id: UUID) -> Place | None:
        return next((place for place in self._places if place.id == place_id), None)

    def save(self, place: Place) -> None:
        self._places.append(place)

    def update(self, place: Place) -> None:
        self._places = [place if p.id == place.id else p for p in self._places]

    def delete(self, place_id: UUID) -> None:
        self._places = [place for place in self._places if place.id != place_id]

    def _filter(
        self,
        category: str | None,
        city_id: int | None,
        min_rating: float | None,
        max_cost: float | None,
    ) -> list[Place]:
        places = [place for place in self._places if not place.archived]

        if category is not None:
            places = [place for place in places if place.category == category]
        if city_id is not None:
            places = [place for place in places if place.city_id == city_id]
        if min_rating is not None:
            places = [place for place in places if place.average_rating >= min_rating]
        if max_cost is not None:
            places = [place for place in places if place.cost <= max_cost]

        return places

    def _sort(self, places: list[Place], sort: str) -> list[Place]:
        if sort == "cost":
            return sorted(places, key=lambda place: (place.cost, place.name, place.id))
        if sort == "rating":
            return sorted(places, key=lambda place: (-place.average_rating, place.name, place.id))

        return sorted(places, key=lambda place: (place.name, place.id))
