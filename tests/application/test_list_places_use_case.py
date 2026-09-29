from recomendacoes_api.application.use_cases import ListPlacesUseCase
from recomendacoes_api.domain.entities import Place
from tests.adapters.database.mock_place_repository import MockPlaceRepository


def test_list_places_paginated_returns_total_and_items():
    place1 = Place.create("Place 1", "Natureza", 4.0, 1.0, 10.0)
    place2 = Place.create("Place 2", "Monumento", 5.0, 2.0, 20.0)
    place3 = Place.create("Place 3", "Praia", 4.5, 3.0, 30.0)

    repo = MockPlaceRepository([place1, place2, place3])
    use_case = ListPlacesUseCase(repo)

    total, items = use_case.execute(limit=2, offset=1)

    assert total == 3
    assert len(items) == 2
    assert items[0] == place2
    assert items[1] == place3
