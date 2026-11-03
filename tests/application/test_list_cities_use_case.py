from recomendacoes_api.application.use_cases import ListCitiesUseCase
from recomendacoes_api.domain.entities import City
from tests.adapters.database.mock_city_repository import MockCityRepository

CITIES = [
    City(id=4314902, name="Porto Alegre", state_code="RS"),
    City(id=4205407, name="Florianópolis", state_code="SC"),
]


def build_use_case() -> ListCitiesUseCase:
    return ListCitiesUseCase(MockCityRepository(CITIES))


def test_list_cities_without_filter_returns_all_cities():
    assert build_use_case().execute() == CITIES


def test_list_cities_returns_only_cities_of_the_state():
    assert build_use_case().execute("RS") == [CITIES[0]]


def test_list_cities_accepts_lowercase_state_code():
    assert build_use_case().execute("sc") == [CITIES[1]]


def test_list_cities_of_unknown_state_returns_empty_list():
    assert build_use_case().execute("XX") == []
