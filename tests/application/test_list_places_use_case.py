from recomendacoes_api.application.use_cases import ListPlacesUseCase
from recomendacoes_api.domain.entities import Place
from tests.adapters.database.mock_place_repository import MockPlaceRepository


def build_places(count: int) -> list[Place]:
    return [
        Place.create(name=f"Place {i}", category="beach", city_id=4207304, rating=4.5, cost=30.0)
        for i in range(count)
    ]


def test_list_places_returns_a_page_with_the_places_and_the_total():
    places = build_places(2)
    use_case = ListPlacesUseCase(MockPlaceRepository(places))

    page = use_case.execute()

    assert page.items == places
    assert page.total == 2


def test_list_places_applies_limit_and_offset_but_keeps_the_full_total():
    places = build_places(5)
    use_case = ListPlacesUseCase(MockPlaceRepository(places))

    page = use_case.execute(limit=2, offset=1)

    assert page.items == places[1:3]
    assert page.total == 5


def test_list_places_beyond_the_last_page_returns_no_items():
    use_case = ListPlacesUseCase(MockPlaceRepository(build_places(2)))

    page = use_case.execute(limit=10, offset=10)

    assert page.items == []
    assert page.total == 2
