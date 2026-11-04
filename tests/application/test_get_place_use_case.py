from uuid import uuid4

import pytest

from recomendacoes_api.application.use_cases import GetPlaceUseCase
from recomendacoes_api.domain.entities import Place
from recomendacoes_api.domain.exceptions import PlaceNotFoundError
from tests.adapters.database.mock_place_repository import MockPlaceRepository


def test_get_place_returns_the_place_when_found_and_active():
    place = Place(
        name="Praia do Rosa",
        category="beach",
        city_id=4207304,
        cost=30.0,
        average_rating=4.5,
        review_count=2,
    )
    use_case = GetPlaceUseCase(MockPlaceRepository([place]))

    result = use_case.execute(place.id)

    assert result == place


def test_get_place_raises_not_found_when_missing():
    use_case = GetPlaceUseCase(MockPlaceRepository())

    with pytest.raises(PlaceNotFoundError):
        use_case.execute(uuid4())


def test_get_place_raises_not_found_when_archived():
    place = Place(
        name="Praia do Rosa",
        category="beach",
        city_id=4207304,
        cost=30.0,
        archived=True,
    )
    use_case = GetPlaceUseCase(MockPlaceRepository([place]))

    with pytest.raises(PlaceNotFoundError):
        use_case.execute(place.id)
