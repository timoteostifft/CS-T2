from recomendacoes_api.application.use_cases import ListPlacesUseCase
from recomendacoes_api.domain.entities import Place
from tests.adapters.database.mock_place_repository import MockPlaceRepository


def test_list_places_returns_places_from_repository():
    places = [
        Place.create(name="Praia do Rosa", category="beach", city_id=4207304, rating=4.5, cost=30.0)
    ]
    use_case = ListPlacesUseCase(MockPlaceRepository(places))

    result = use_case.execute()

    assert result == places
