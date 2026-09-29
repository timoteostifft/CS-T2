from recomendacoes_api.application.use_cases import CreatePlaceUseCase
from tests.adapters.database.mock_place_repository import MockPlaceRepository


def test_create_place_saves_and_returns_place():
    repository = MockPlaceRepository()
    use_case = CreatePlaceUseCase(repository)

    place = use_case.execute(
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
    assert len(repository.list_all()) == 1
    assert repository.list_all()[0] == place
