from recomendacoes_api.application.use_cases import ListCitiesUseCase
from recomendacoes_api.domain.entities import City
from tests.adapters.database.mock_city_repository import MockCityRepository

CITIES = [
    City(id=4314902, name="Porto Alegre", state_code="RS"),
    City(id=4205407, name="Florianópolis", state_code="SC"),
    City(id=4207304, name="Imbituba", state_code="SC"),
]


def build_use_case() -> ListCitiesUseCase:
    return ListCitiesUseCase(MockCityRepository(CITIES))


def test_list_cities_without_filter_returns_all_cities_and_the_total():
    page = build_use_case().execute()

    assert page.items == CITIES
    assert page.total == 3


def test_list_cities_returns_only_cities_of_the_state():
    page = build_use_case().execute("SC")

    assert page.items == CITIES[1:]
    assert page.total == 2


def test_list_cities_accepts_lowercase_state_code():
    page = build_use_case().execute("rs")

    assert page.items == [CITIES[0]]


def test_list_cities_of_unknown_state_returns_empty_page():
    page = build_use_case().execute("XX")

    assert page.items == []
    assert page.total == 0


def test_list_cities_applies_limit_and_offset_within_the_filter():
    page = build_use_case().execute("SC", limit=1, offset=1)

    assert page.items == [CITIES[2]]
    assert page.total == 2
