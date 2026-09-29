from uuid import uuid4

from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import (
    create_access_token,
    get_get_place_by_id_use_case,
    get_list_places_use_case,
)
from recomendacoes_api.app import app
from recomendacoes_api.domain.exceptions import (
    DomainError,
    InvalidPlaceError,
    PlaceNotFoundError,
)


class RaisingInvalidPlaceUseCase:
    def execute(self, limit: int = 10, offset: int = 0):
        raise InvalidPlaceError("Place name must not be empty")


class RaisingPlaceNotFoundUseCase:
    def execute(self, id):
        raise PlaceNotFoundError("Place not found")


class RaisingDomainErrorUseCase:
    def execute(self, limit: int = 10, offset: int = 0):
        raise DomainError("General domain issue")


def _auth_headers() -> dict[str, str]:
    token = create_access_token({"sub": "test_user"})
    return {"Authorization": f"Bearer {token}"}


def test_invalid_place_error_is_translated_to_400():
    app.dependency_overrides[get_list_places_use_case] = lambda: RaisingInvalidPlaceUseCase()

    client = TestClient(app)
    response = client.get("/api/v1/places", headers=_auth_headers())

    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "message": "Place name must not be empty",
    }


def test_place_not_found_error_is_translated_to_404():
    app.dependency_overrides[get_get_place_by_id_use_case] = lambda: RaisingPlaceNotFoundUseCase()

    client = TestClient(app)
    response = client.get(f"/api/v1/places/{uuid4()}", headers=_auth_headers())

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "message": "Place not found",
    }


def test_missing_token_is_translated_to_401():
    client = TestClient(app)
    response = client.get("/api/v1/places")

    assert response.status_code == 401
    assert response.json() == {
        "code": 401,
        "message": "Token JWT ausente, inválido ou expirado.",
    }


def test_unhandled_domain_error_falls_back_to_400():
    app.dependency_overrides[get_list_places_use_case] = lambda: RaisingDomainErrorUseCase()

    client = TestClient(app)
    response = client.get("/api/v1/places", headers=_auth_headers())

    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "message": "General domain issue",
    }
