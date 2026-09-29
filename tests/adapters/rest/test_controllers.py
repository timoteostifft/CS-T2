from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import (
    create_access_token,
    get_create_place_use_case,
    get_delete_place_use_case,
    get_get_place_by_id_use_case,
    get_list_places_use_case,
    get_rank_places_use_case,
    get_update_place_use_case,
)
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import (
    CreatePlaceUseCase,
    DeletePlaceUseCase,
    GetPlaceByIdUseCase,
    ListPlacesUseCase,
    RankPlacesUseCase,
    UpdatePlaceUseCase,
)
from recomendacoes_api.domain.entities import Place
from tests.adapters.database.mock_place_repository import MockPlaceRepository


def _auth_headers() -> dict[str, str]:
    token = create_access_token({"sub": "tester"})
    return {"Authorization": f"Bearer {token}"}


def test_list_places_paginated_returns_json():
    places = [
        Place.create(
            name="Torre de Belém", category="Monumento", rating=4.7, cost=3.0, popularity=9.5
        ),
        Place.create(name="Gerês", category="Natureza", rating=4.9, cost=1.0, popularity=8.0),
    ]
    use_case = ListPlacesUseCase(MockPlaceRepository(places))
    app.dependency_overrides[get_list_places_use_case] = lambda: use_case

    client = TestClient(app)
    response = client.get("/api/v1/places?limit=10&offset=0", headers=_auth_headers())

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["items"][0]["name"] == "Torre de Belém"
    assert body["items"][0]["category"] == "Monumento"
    assert body["items"][0]["rating"] == 4.7
    assert body["items"][0]["cost"] == 3.0
    assert body["items"][0]["popularity"] == 9.5


def test_create_place_returns_201():
    repository = MockPlaceRepository()
    use_case = CreatePlaceUseCase(repository)
    app.dependency_overrides[get_create_place_use_case] = lambda: use_case

    client = TestClient(app)
    response = client.post(
        "/api/v1/places",
        json={
            "name": "Torre de Belém",
            "category": "Monumento",
            "rating": 4.7,
            "cost": 3.0,
            "popularity": 9.5,
        },
        headers=_auth_headers(),
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Torre de Belém"
    assert body["category"] == "Monumento"
    assert body["rating"] == 4.7
    assert body["cost"] == 3.0
    assert body["popularity"] == 9.5
    assert "id" in body


def test_get_place_by_id_returns_place():
    place = Place.create("Peneda-Gerês", "Natureza", 4.8, 2.5, 9.0)
    use_case = GetPlaceByIdUseCase(MockPlaceRepository([place]))
    app.dependency_overrides[get_get_place_by_id_use_case] = lambda: use_case

    client = TestClient(app)
    response = client.get(f"/api/v1/places/{place.id}", headers=_auth_headers())

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(place.id)
    assert body["name"] == "Peneda-Gerês"


def test_update_place_returns_updated_place():
    place = Place.create("Torre de Belém", "Monumento", 4.7, 3.0, 9.5)
    use_case = UpdatePlaceUseCase(MockPlaceRepository([place]))
    app.dependency_overrides[get_update_place_use_case] = lambda: use_case

    client = TestClient(app)
    response = client.put(
        f"/api/v1/places/{place.id}",
        json={"name": "Torre de Belém (Atualizado)", "rating": 4.9},
        headers=_auth_headers(),
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Torre de Belém (Atualizado)"
    assert body["rating"] == 4.9


def test_delete_place_returns_204():
    place = Place.create("Torre de Belém", "Monumento", 4.7, 3.0, 9.5)
    use_case = DeletePlaceUseCase(MockPlaceRepository([place]))
    app.dependency_overrides[get_delete_place_use_case] = lambda: use_case

    client = TestClient(app)
    response = client.delete(f"/api/v1/places/{place.id}", headers=_auth_headers())

    app.dependency_overrides.clear()

    assert response.status_code == 204


def test_rank_places_returns_ordered_places_with_score_final():
    place1 = Place.create("Barato", "Natureza", rating=4.0, cost=1.0, popularity=5.0)
    place2 = Place.create("Popular", "Monumento", rating=4.8, cost=5.0, popularity=10.0)
    use_case = RankPlacesUseCase(MockPlaceRepository([place1, place2]))
    app.dependency_overrides[get_rank_places_use_case] = lambda: use_case

    client = TestClient(app)
    response = client.post(
        "/api/v1/places/rank?limit=5",
        json={"weights": {"rating": 0.6, "cost": -0.3, "popularity": 0.1}},
        headers=_auth_headers(),
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert "score_final" in body[0]
    assert "score_final" in body[1]
    assert body[0]["score_final"] >= body[1]["score_final"]


def test_unauthorized_request_without_token():
    client = TestClient(app)
    response = client.get("/api/v1/places")

    assert response.status_code == 401
    assert response.json()["code"] == 401
