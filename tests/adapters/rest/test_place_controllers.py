from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import (
    get_create_place_use_case,
    get_list_places_use_case,
)
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import CreatePlaceUseCase, ListPlacesUseCase
from recomendacoes_api.domain.entities import City, Place
from tests.adapters.database.mock_city_repository import MockCityRepository
from tests.adapters.database.mock_place_repository import MockPlaceRepository

CITY = City(id=4207304, name="Imbituba", state_code="SC")
VALID_BODY = {
    "name": "Praia do Rosa",
    "category": "beach",
    "city_id": CITY.id,
    "rating": 4.5,
    "cost": 30.0,
}


def list_places(places: list[Place]):
    use_case = ListPlacesUseCase(MockPlaceRepository(places))
    app.dependency_overrides[get_list_places_use_case] = lambda: use_case

    response = TestClient(app).get("/api/v1/places")

    app.dependency_overrides.clear()

    return response


def create_place(body: dict, places: MockPlaceRepository | None = None):
    use_case = CreatePlaceUseCase(places or MockPlaceRepository(), MockCityRepository([CITY]))
    app.dependency_overrides[get_create_place_use_case] = lambda: use_case

    response = TestClient(app).post("/api/v1/places", json=body)

    app.dependency_overrides.clear()

    return response


def test_list_places_returns_places_as_json():
    place = Place.create(
        name="Praia do Rosa", category="beach", city_id=CITY.id, rating=4.5, cost=30.0
    )

    response = list_places([place])

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Praia do Rosa"
    assert body[0]["category"] == "beach"
    assert body[0]["city_id"] == CITY.id
    assert body[0]["rating"] == 4.5
    assert body[0]["cost"] == 30.0


def test_create_place_returns_201_and_the_created_place():
    places = MockPlaceRepository()

    response = create_place(VALID_BODY, places)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Praia do Rosa"
    assert body["category"] == "beach"
    assert body["city_id"] == CITY.id
    assert body["rating"] == 4.5
    assert body["cost"] == 30.0
    assert body["id"]
    assert places.count_all() == 1


def test_create_place_with_unknown_city_returns_400():
    response = create_place({**VALID_BODY, "city_id": 1})

    assert response.status_code == 400
    assert response.json() == {
        "error": "bad_request",
        "code": 400,
        "message": "City 1 does not exist",
    }


def test_create_place_with_blank_name_returns_400():
    response = create_place({**VALID_BODY, "name": " "})

    assert response.status_code == 400
    assert response.json()["error"] == "bad_request"


def test_create_place_with_rating_out_of_range_returns_422():
    assert create_place({**VALID_BODY, "rating": 6}).status_code == 422


def test_create_place_with_missing_field_returns_422():
    body = {key: value for key, value in VALID_BODY.items() if key != "cost"}

    assert create_place(body).status_code == 422
