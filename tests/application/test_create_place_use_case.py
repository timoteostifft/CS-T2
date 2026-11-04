import pytest

from recomendacoes_api.application.use_cases import CreatePlaceUseCase
from recomendacoes_api.domain.entities import City
from recomendacoes_api.domain.exceptions import InvalidPlaceError
from tests.adapters.database.mock_city_repository import MockCityRepository
from tests.adapters.database.mock_place_repository import MockPlaceRepository

CITY = City(id=4207304, name="Imbituba", state_code="SC")


def build_use_case(places: MockPlaceRepository) -> CreatePlaceUseCase:
    return CreatePlaceUseCase(places, MockCityRepository([CITY]))


def test_create_place_saves_and_returns_the_place_with_zero_reviews():
    places = MockPlaceRepository()

    place = build_use_case(places).execute(
        name="Praia do Rosa", category="beach", city_id=CITY.id, cost=30.0
    )

    assert place.name == "Praia do Rosa"
    assert place.average_rating == 0.0
    assert place.review_count == 0
    assert places.find_by_id(place.id) == place


def test_create_place_with_unknown_city_raises_and_saves_nothing():
    places = MockPlaceRepository()
    use_case = build_use_case(places)

    with pytest.raises(InvalidPlaceError):
        use_case.execute(name="Praia do Rosa", category="beach", city_id=1, cost=30.0)

    assert places.count_all() == 0


def test_create_place_with_invalid_data_raises_and_saves_nothing():
    places = MockPlaceRepository()
    use_case = build_use_case(places)

    with pytest.raises(InvalidPlaceError):
        use_case.execute(name=" ", category="beach", city_id=CITY.id, cost=30.0)

    assert places.count_all() == 0
