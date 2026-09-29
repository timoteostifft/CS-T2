import pytest

from recomendacoes_api.domain.entities import Place
from recomendacoes_api.domain.exceptions import InvalidPlaceError


def test_create_place():
    place = Place.create(
        name="Torre de Belém",
        category="Monumento",
        rating=4.7,
        cost=3.0,
        popularity=9.5,
    )

    assert place.name == "Torre de Belém"
    assert place.category == "Monumento"
    assert place.rating == 4.7
    assert place.cost == 3.0
    assert place.popularity == 9.5
    assert place.id is not None


def test_create_place_with_blank_name_raises_invalid_place_error():
    with pytest.raises(InvalidPlaceError):
        Place.create(
            name="  ",
            category="Monumento",
            rating=4.7,
            cost=3.0,
            popularity=9.5,
        )


def test_create_place_with_blank_category_raises_invalid_place_error():
    with pytest.raises(InvalidPlaceError):
        Place.create(
            name="Torre de Belém",
            category="  ",
            rating=4.7,
            cost=3.0,
            popularity=9.5,
        )


def test_create_place_with_negative_rating_raises_invalid_place_error():
    with pytest.raises(InvalidPlaceError):
        Place.create(
            name="Torre de Belém",
            category="Monumento",
            rating=-1.0,
            cost=3.0,
            popularity=9.5,
        )


def test_create_place_with_negative_cost_raises_invalid_place_error():
    with pytest.raises(InvalidPlaceError):
        Place.create(
            name="Torre de Belém",
            category="Monumento",
            rating=4.7,
            cost=-1.0,
            popularity=9.5,
        )


def test_create_place_with_negative_popularity_raises_invalid_place_error():
    with pytest.raises(InvalidPlaceError):
        Place.create(
            name="Torre de Belém",
            category="Monumento",
            rating=4.7,
            cost=3.0,
            popularity=-2.0,
        )
