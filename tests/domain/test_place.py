import pytest

from recomendacoes_api.domain.entities import Place
from recomendacoes_api.domain.exceptions import InvalidPlaceError


def build_place(**overrides) -> Place:
    data = {
        "name": "Praia do Rosa",
        "category": "beach",
        "city_id": 4207304,
        "rating": 4.5,
        "cost": 30.0,
    }

    return Place.create(**{**data, **overrides})


def test_create_place():
    place = build_place()

    assert place.name == "Praia do Rosa"
    assert place.city_id == 4207304
    assert place.rating == 4.5
    assert place.cost == 30.0
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


@pytest.mark.parametrize("rating", [-0.1, 5.1])
def test_create_place_with_rating_out_of_range_raises_invalid_place_error(rating):
    with pytest.raises(InvalidPlaceError):
        build_place(rating=rating)


@pytest.mark.parametrize("rating", [0, 5])
def test_create_place_accepts_rating_bounds(rating):
    assert build_place(rating=rating).rating == rating


def test_create_place_with_negative_cost_raises_invalid_place_error():
    with pytest.raises(InvalidPlaceError):
        build_place(cost=-1)


def test_create_place_accepts_free_place():
    assert build_place(cost=0).cost == 0
