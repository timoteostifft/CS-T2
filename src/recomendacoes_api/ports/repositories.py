from typing import Protocol

from recomendacoes_api.domain.entities import City, Place, State


class PlaceRepository(Protocol):
    def list_all(self) -> list[Place]: ...


class StateRepository(Protocol):
    def list_all(self) -> list[State]: ...


class CityRepository(Protocol):
    def list_all(self, state_code: str | None = None) -> list[City]: ...
