from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import get_list_places_use_case
from recomendacoes_api.app import app
from recomendacoes_api.domain.exceptions import DomainError, InvalidPlaceError, PlaceNotFoundError


def raising(error: Exception):
    class RaisingUseCase:
        def execute(self):
            raise error

    return RaisingUseCase()


def get_places_with(error: Exception):
    app.dependency_overrides[get_list_places_use_case] = lambda: raising(error)

    response = TestClient(app).get("/api/v1/places")

    app.dependency_overrides.clear()

    return response


def test_invalid_place_error_is_translated_to_400():
    response = get_places_with(InvalidPlaceError("Place name must not be empty"))

    assert response.status_code == 400
    assert response.json() == {
        "error": "bad_request",
        "code": 400,
        "message": "Place name must not be empty",
    }


def test_place_not_found_error_is_translated_to_404():
    response = get_places_with(PlaceNotFoundError("Place not found"))

    assert response.status_code == 404
    assert response.json() == {"error": "not_found", "code": 404, "message": "Place not found"}


def test_unmapped_domain_error_falls_back_to_400():
    response = get_places_with(DomainError("Something is wrong"))

    assert response.status_code == 400
    assert response.json() == {"error": "bad_request", "code": 400, "message": "Something is wrong"}
