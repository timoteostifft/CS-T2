from uuid import UUID

from recomendacoes_api.domain.entities import Place


class MockPlaceRepository:
    def __init__(self, places: list[Place] | None = None) -> None:
        self._places = places or []

    def list_paginated(self, limit: int, offset: int) -> tuple[int, list[Place]]:
        total = len(self._places)
        items = self._places[offset : offset + limit]
        return total, items

    def list_all(self) -> list[Place]:
        return list(self._places)

    def find_by_id(self, id: UUID) -> Place | None:
        for place in self._places:
            if place.id == id:
                return place
        return None

    def save(self, place: Place) -> Place:
        self._places.append(place)
        return place

    def update(self, place: Place) -> Place:
        for idx, existing in enumerate(self._places):
            if existing.id == place.id:
                self._places[idx] = place
                return place
        return place

    def delete(self, id: UUID) -> bool:
        for idx, place in enumerate(self._places):
            if place.id == id:
                self._places.pop(idx)
                return True
        return False
