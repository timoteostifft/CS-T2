import pytest

from recomendacoes_api.domain.entities import Place
from recomendacoes_api.domain.exceptions import InvalidPlaceError


def test_create_place():
    place = Place.create(name="Praia do Rosa", city="Imbituba", category="beach")

    assert place.name == "Praia do Rosa"
    assert place.id is not None


def test_create_place_with_blank_name_raises_invalid_place_error():
    with pytest.raises(InvalidPlaceError):
        Place.create(name="  ", city="Imbituba", category="beach")


def test_create_place_with_blank_city_raises_invalid_place_error():
    with pytest.raises(InvalidPlaceError):
        Place.create(name="Praia do Rosa", city="  ", category="beach")
