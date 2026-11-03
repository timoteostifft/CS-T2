from uuid import UUID

from recomendacoes_api.domain.entities import Place


class MockPlaceRepository:
    def __init__(self, places: list[Place] | None = None) -> None:
        self._places = list(places or [])

    def list_all(self, limit: int | None = None, offset: int = 0) -> list[Place]:
        end = None if limit is None else offset + limit

        return self._places[offset:end]

    def count_all(self) -> int:
        return len(self._places)

    def find_by_id(self, place_id: UUID) -> Place | None:
        return next((place for place in self._places if place.id == place_id), None)

    def save(self, place: Place) -> None:
        self._places.append(place)

    def update(self, place: Place) -> None:
        self._places = [place if p.id == place.id else p for p in self._places]

    def delete(self, place_id: UUID) -> None:
        self._places = [place for place in self._places if place.id != place_id]
