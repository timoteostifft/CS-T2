from recomendacoes_api.application.use_cases import ListPlacesUseCase
from recomendacoes_api.domain.entities import Place
from tests.adapters.database.mock_place_repository import MockPlaceRepository


def test_list_places_returns_places_from_repository():
    places = [Place.create(name="Praia do Rosa", city="Imbituba", category="beach")]
    use_case = ListPlacesUseCase(MockPlaceRepository(places))

    result = use_case.execute()

    assert result == places
