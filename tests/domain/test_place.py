import pytest

from recomendacoes_api.domain.entities import Place
from recomendacoes_api.domain.exceptions import InvalidPlaceError


def build_place(**overrides) -> Place:
    data = {
        "name": "Praia do Rosa",
        "category": "beach",
        "city_id": 4207304,
        "cost": 30.0,
    }

    return Place(**{**data, **overrides})


def test_create_place():
    place = Place.create(name="Praia do Rosa", category="beach", city_id=4207304, cost=30.0)

    assert place.name == "Praia do Rosa"
    assert place.category == "beach"
    assert place.city_id == 4207304
    assert place.cost == 30.0
    assert place.average_rating == 0.0
    assert place.review_count == 0
    assert place.archived is False
    assert place.id is not None


def test_create_place_generates_distinct_ids():
    first = build_place()
    second = build_place()

    assert first.id != second.id


@pytest.mark.parametrize("field", ["name", "category"])
def test_create_place_with_blank_text_raises_invalid_place_error(field):
    with pytest.raises(InvalidPlaceError):
        build_place(**{field: "  "})


@pytest.mark.parametrize("city_id", [0, -1])
def test_create_place_with_non_positive_city_id_raises_invalid_place_error(city_id):
    with pytest.raises(InvalidPlaceError):
        build_place(city_id=city_id)


@pytest.mark.parametrize("average_rating", [-0.1, 5.1])
def test_create_place_with_average_rating_out_of_range_raises_invalid_place_error(average_rating):
    with pytest.raises(InvalidPlaceError):
        build_place(average_rating=average_rating)


@pytest.mark.parametrize("average_rating", [0, 5])
def test_create_place_accepts_average_rating_bounds(average_rating):
    assert build_place(average_rating=average_rating).average_rating == average_rating


def test_create_place_with_negative_review_count_raises_invalid_place_error():
    with pytest.raises(InvalidPlaceError):
        build_place(review_count=-1)


def test_create_place_with_negative_cost_raises_invalid_place_error():
    with pytest.raises(InvalidPlaceError):
        build_place(cost=-1)


def test_create_place_accepts_free_place():
    assert build_place(cost=0).cost == 0


def test_recalculate_rating_updates_average_and_count():
    place = build_place()

    place.recalculate_rating([4, 5, 3])

    assert place.review_count == 3
    assert place.average_rating == 4.0


def test_recalculate_rating_with_empty_list_resets_to_zero():
    place = build_place(average_rating=4.5, review_count=2)

    place.recalculate_rating([])

    assert place.review_count == 0
    assert place.average_rating == 0.0
