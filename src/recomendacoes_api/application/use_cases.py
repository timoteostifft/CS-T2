from recomendacoes_api.domain.entities import City, Place, State
from recomendacoes_api.ports.repositories import CityRepository, PlaceRepository, StateRepository


class ListPlacesUseCase:
    def __init__(self, place_repository: PlaceRepository) -> None:
        self._place_repository = place_repository

    def execute(self) -> list[Place]:
        return self._place_repository.list_all()


class ListStatesUseCase:
    def __init__(self, state_repository: StateRepository) -> None:
        self._state_repository = state_repository

    def execute(self) -> list[State]:
        return self._state_repository.list_all()


class ListCitiesUseCase:
    def __init__(self, city_repository: CityRepository) -> None:
        self._city_repository = city_repository

    def execute(self, state_code: str | None = None) -> list[City]:
        code = state_code.upper() if state_code else None
        
        return self._city_repository.list_all(code)
