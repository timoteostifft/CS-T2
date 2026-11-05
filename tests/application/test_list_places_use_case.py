import pytest

from recomendacoes_api.application.use_cases import ListPlacesUseCase
from recomendacoes_api.domain.entities import Place
from recomendacoes_api.domain.exceptions import InvalidPlaceError
from tests.adapters.database.mock_place_repository import MockPlaceRepository


def build_places(count: int) -> list[Place]:
    return [
        Place(
            name=f"Place {i}",
            category="beach",
            city_id=4207304,
            cost=30.0,
            average_rating=4.5,
            review_count=1,
        )
        for i in range(count)
    ]


def test_list_places_returns_a_page_with_the_places_and_the_total():
    places = build_places(2)
    use_case = ListPlacesUseCase(MockPlaceRepository(places))

    page = use_case.execute()

    assert page.items == places
    assert page.total == 2


def test_list_places_excludes_archived_places():
    active = Place.create(name="Active", category="beach", city_id=4207304, cost=10.0)
    archived = Place(
        name="Archived",
        category="beach",
        city_id=4207304,
        cost=10.0,
        archived=True,
    )
    use_case = ListPlacesUseCase(MockPlaceRepository([active, archived]))

    page = use_case.execute()

    assert page.items == [active]
    assert page.total == 1


def test_list_places_filters_by_category_city_min_rating_and_max_cost():
    match = Place(
        name="Match",
        category="trail",
        city_id=10,
        cost=20.0,
        average_rating=4.5,
        review_count=2,
    )
    other = Place(
        name="Other",
        category="beach",
        city_id=10,
        cost=20.0,
        average_rating=4.5,
        review_count=2,
    )
    use_case = ListPlacesUseCase(MockPlaceRepository([match, other]))

    page = use_case.execute(category="trail", city_id=10, min_rating=4.0, max_cost=30.0)

    assert page.items == [match]
    assert page.total == 1


def test_list_places_sorts_by_rating_cost_or_name():
    cheap = Place(name="B Place", category="beach", city_id=1, cost=10.0, average_rating=3.0)
    top = Place(name="C Place", category="beach", city_id=1, cost=50.0, average_rating=5.0)
    first_alpha = Place(name="A Place", category="beach", city_id=1, cost=30.0, average_rating=4.0)
    use_case = ListPlacesUseCase(MockPlaceRepository([cheap, top, first_alpha]))

    assert [p.name for p in use_case.execute(sort="name").items] == [
        "A Place",
        "B Place",
        "C Place",
    ]
    assert [p.name for p in use_case.execute(sort="cost").items] == [
        "B Place",
        "A Place",
        "C Place",
    ]
    assert [p.name for p in use_case.execute(sort="rating").items] == [
        "C Place",
        "A Place",
        "B Place",
    ]


def test_list_places_with_invalid_sort_raises_invalid_place_error():
    use_case = ListPlacesUseCase(MockPlaceRepository())

    with pytest.raises(InvalidPlaceError):
        use_case.execute(sort="distance")


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
