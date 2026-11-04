from typing import Protocol
from uuid import UUID

from recomendacoes_api.domain.entities import City, Place, Review, State


class PlaceRepository(Protocol):
    def list_all(
        self,
        category: str | None = None,
        city_id: int | None = None,
        min_rating: float | None = None,
        max_cost: float | None = None,
        sort: str = "name",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Place]: ...

    def count_all(
        self,
        category: str | None = None,
        city_id: int | None = None,
        min_rating: float | None = None,
        max_cost: float | None = None,
    ) -> int: ...

    def find_by_id(self, place_id: UUID) -> Place | None: ...

    def save(self, place: Place) -> None: ...

    def update(self, place: Place) -> None: ...

    def delete(self, place_id: UUID) -> None: ...


class ReviewRepository(Protocol):
    def find_by_place_and_device(self, place_id: UUID, device_id: str) -> Review | None: ...

    def list_by_place(self, place_id: UUID) -> list[Review]: ...

    def save(self, review: Review) -> None: ...

    def update(self, review: Review) -> None: ...


class StateRepository(Protocol):
    def list_all(self, limit: int | None = None, offset: int = 0) -> list[State]: ...

    def count_all(self) -> int: ...


class CityRepository(Protocol):
    def list_all(
        self, state_code: str | None = None, limit: int | None = None, offset: int = 0
    ) -> list[City]: ...

    def count_all(self, state_code: str | None = None) -> int: ...

    def exists_by_id(self, city_id: int) -> bool: ...
