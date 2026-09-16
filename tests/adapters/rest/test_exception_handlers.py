from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import get_list_places_use_case
from recomendacoes_api.app import app
from recomendacoes_api.domain.exceptions import InvalidPlaceError


class RaisingUseCase:
    def execute(self):
        raise InvalidPlaceError("Place name must not be empty")


def test_invalid_place_error_is_translated_to_400():
    app.dependency_overrides[get_list_places_use_case] = lambda: RaisingUseCase()

    client = TestClient(app)
    response = client.get("/places")

    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json() == {
        "error": "bad_request",
        "message": "Place name must not be empty",
    }
