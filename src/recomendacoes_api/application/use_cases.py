from recomendacoes_api.domain.entities import City, Place, State
from recomendacoes_api.domain.exceptions import InvalidPlaceError
from recomendacoes_api.ports.repositories import CityRepository, PlaceRepository, StateRepository


class ListPlacesUseCase:
    def __init__(self, place_repository: PlaceRepository) -> None:
        self._place_repository = place_repository

    def execute(self) -> list[Place]:
        return self._place_repository.list_all()


class CreatePlaceUseCase:
    def __init__(self, place_repository: PlaceRepository, city_repository: CityRepository) -> None:
        self._place_repository = place_repository
        self._city_repository = city_repository

    def execute(self, name: str, category: str, city_id: int, rating: float, cost: float) -> Place:
        place = Place.create(
            name=name, category=category, city_id=city_id, rating=rating, cost=cost
        )

        if not self._city_repository.exists_by_id(city_id):
            raise InvalidPlaceError(f"City {city_id} does not exist")

        self._place_repository.save(place)

        return place


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
