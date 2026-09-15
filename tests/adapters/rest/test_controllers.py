from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import get_list_places_use_case
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import ListPlacesUseCase
from recomendacoes_api.domain.entities import Place
from tests.adapters.database.mock_place_repository import MockPlaceRepository


def test_list_places_returns_places_as_json():
    places = [Place.create(name="Praia do Rosa", city="Imbituba", category="beach")]
    use_case = ListPlacesUseCase(MockPlaceRepository(places))
    app.dependency_overrides[get_list_places_use_case] = lambda: use_case

    client = TestClient(app)
    response = client.get("/places")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Praia do Rosa"
    assert body[0]["city"] == "Imbituba"
    assert body[0]["category"] == "beach"
