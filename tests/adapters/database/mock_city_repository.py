from recomendacoes_api.domain.entities import City


class MockCityRepository:
    def __init__(self, cities: list[City] | None = None) -> None:
        self._cities = cities or []

    def list_all(self, state_code: str | None = None) -> list[City]:
        if state_code is None:
            return self._cities

        return [city for city in self._cities if city.state_code == state_code]

    def exists_by_id(self, city_id: int) -> bool:
        return any(city.id == city_id for city in self._cities)
