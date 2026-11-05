from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import (
    get_create_trip_use_case,
    get_current_user,
    get_delete_trip_use_case,
    get_get_trip_use_case,
    get_list_trips_use_case,
    get_update_trip_use_case,
)
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import (
    CreateTripUseCase,
    DeleteTripUseCase,
    GetTripUseCase,
    ListTripsUseCase,
    UpdateTripUseCase,
)
from recomendacoes_api.domain.entities import Trip, User
from tests.adapters.database.mock_trip_repository import MockTripRepository

USER = User.create(name="Ana", email="ana@example.com", password_hash="hash")
BODY = {
    "name": "Beach trip",
    "description": "Sun",
    "start_date": "2026-12-01",
    "end_date": "2026-12-10",
}


def make_trip(owner: User = USER, name: str = "Beach trip") -> Trip:
    return Trip.create(name, "Sun", date(2026, 12, 1), date(2026, 12, 10), owner.id)


def call(method: str, path: str, dependency, use_case_type, trips=None, **kwargs):
    repository = MockTripRepository(trips)
    app.dependency_overrides[get_current_user] = lambda: USER
    app.dependency_overrides[dependency] = lambda: use_case_type(repository)

    response = TestClient(app).request(method, f"/api/v1/trips{path}", **kwargs)

    app.dependency_overrides.clear()

    return response


def create_trip(body: dict, trips=None):
    return call("POST", "", get_create_trip_use_case, CreateTripUseCase, trips, json=body)


def list_trips(trips=None, query: str = ""):
    return call("GET", query, get_list_trips_use_case, ListTripsUseCase, trips)


def get_trip(trip_id, trips=None):
    return call("GET", f"/{trip_id}", get_get_trip_use_case, GetTripUseCase, trips)


def update_trip(trip_id, body: dict, trips=None):
    return call("PUT", f"/{trip_id}", get_update_trip_use_case, UpdateTripUseCase, trips, json=body)


def delete_trip(trip_id, trips=None):
    return call("DELETE", f"/{trip_id}", get_delete_trip_use_case, DeleteTripUseCase, trips)


def test_create_returns_201_with_the_trip_owned_by_the_user():
    response = create_trip(BODY)

    body = response.json()

    assert response.status_code == 201
    assert body["name"] == "Beach trip"
    assert body["owner_id"] == str(USER.id)
    assert body["start_date"] == "2026-12-01"


def test_create_with_end_before_start_returns_400():
    response = create_trip({**BODY, "end_date": "2026-11-01"})

    assert response.status_code == 400
    assert response.json()["error"] == "bad_request"


def test_create_with_missing_dates_returns_422():
    assert create_trip({"name": "Trip"}).status_code == 422


def test_create_without_authentication_returns_401():
    response = TestClient(app).post("/api/v1/trips", json=BODY)

    assert response.status_code == 401


def test_list_returns_a_page_with_only_the_user_trips():
    trips = [
        make_trip(name="A"),
        make_trip(name="B"),
        make_trip(User.create("Bia", "b@x.com", "h")),
    ]

    response = list_trips(trips, "?limit=1&offset=1")

    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 2
    assert [item["name"] for item in body["items"]] == ["B"]


def test_list_with_invalid_pagination_returns_422():
    assert list_trips(query="?limit=0").status_code == 422


def test_get_returns_the_trip():
    trip = make_trip()

    response = get_trip(trip.id, [trip])

    assert response.status_code == 200
    assert response.json()["id"] == str(trip.id)


def test_get_unknown_trip_returns_404():
    assert get_trip(uuid4()).status_code == 404


def test_get_trip_of_another_user_returns_403():
    trip = make_trip(User.create("Bia", "b@x.com", "h"))

    response = get_trip(trip.id, [trip])

    assert response.status_code == 403
    assert response.json()["error"] == "forbidden"


def test_update_returns_the_updated_trip():
    trip = make_trip()

    response = update_trip(trip.id, {**BODY, "name": "Mountain trip"}, [trip])

    assert response.status_code == 200
    assert response.json()["name"] == "Mountain trip"


def test_update_with_invalid_dates_returns_400():
    trip = make_trip()

    assert update_trip(trip.id, {**BODY, "end_date": "2026-11-01"}, [trip]).status_code == 400


def test_update_trip_of_another_user_returns_403():
    trip = make_trip(User.create("Bia", "b@x.com", "h"))

    assert update_trip(trip.id, BODY, [trip]).status_code == 403


def test_update_unknown_trip_returns_404():
    assert update_trip(uuid4(), BODY).status_code == 404


def test_delete_returns_204_and_removes_the_trip():
    trip = make_trip()

    response = delete_trip(trip.id, [trip])

    assert response.status_code == 204
    assert response.content == b""


def test_delete_trip_of_another_user_returns_403():
    trip = make_trip(User.create("Bia", "b@x.com", "h"))

    assert delete_trip(trip.id, [trip]).status_code == 403


def test_delete_unknown_trip_returns_404():
    assert delete_trip(uuid4()).status_code == 404
