from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import (
    get_add_destination_use_case,
    get_current_user,
    get_delete_destination_use_case,
    get_list_destinations_use_case,
    get_reorder_destinations_use_case,
    get_update_destination_use_case,
)
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import (
    AddDestinationUseCase,
    DeleteDestinationUseCase,
    ListDestinationsUseCase,
    ReorderDestinationsUseCase,
    UpdateDestinationUseCase,
)
from recomendacoes_api.domain.entities import Destination, DestinationCategory, Trip, User
from tests.adapters.database.mock_destination_repository import MockDestinationRepository
from tests.adapters.database.mock_trip_repository import MockTripRepository

USER = User.create(name="Ana", email="ana@example.com", password_hash="hash")
TRIP = Trip.create("Trip", "", date(2026, 12, 1), date(2026, 12, 31), USER.id)
BODY = {
    "name": "Floripa",
    "location": "Florianópolis, SC",
    "category": "beach",
    "arrival_date": "2026-12-01",
    "departure_date": "2026-12-05",
    "photo_url": "http://img/x.png",
    "description": "Sun",
}


def make_destination(position: int = 1, name: str = "Place", trip: Trip = TRIP) -> Destination:
    return Destination.create(
        trip.id,
        name,
        "SC",
        DestinationCategory.CITY,
        date(2026, 12, 1),
        date(2026, 12, 5),
        position,
    )


def call(method: str, path: str, dependency, use_case_type, destinations=None, **kwargs):
    trips, repository = MockTripRepository([TRIP]), MockDestinationRepository(destinations)
    app.dependency_overrides[get_current_user] = lambda: USER
    app.dependency_overrides[dependency] = lambda: use_case_type(trips, repository)

    response = TestClient(app).request(
        method, f"/api/v1/trips/{kwargs.pop('trip_id', TRIP.id)}/destinations{path}", **kwargs
    )

    app.dependency_overrides.clear()

    return response


def add_destination(body: dict, **kwargs):
    return call(
        "POST", "", get_add_destination_use_case, AddDestinationUseCase, json=body, **kwargs
    )


def list_destinations(destinations=None, query: str = ""):
    return call("GET", query, get_list_destinations_use_case, ListDestinationsUseCase, destinations)


def update_destination(destination_id, body: dict, destinations=None):
    return call(
        "PUT",
        f"/{destination_id}",
        get_update_destination_use_case,
        UpdateDestinationUseCase,
        destinations,
        json=body,
    )


def delete_destination(destination_id, destinations=None):
    return call(
        "DELETE",
        f"/{destination_id}",
        get_delete_destination_use_case,
        DeleteDestinationUseCase,
        destinations,
    )


def reorder(ids, destinations=None):
    return call(
        "PUT",
        "/order",
        get_reorder_destinations_use_case,
        ReorderDestinationsUseCase,
        destinations,
        json={"destination_ids": [str(item) for item in ids]},
    )


def test_add_returns_201_with_position_one_on_an_empty_trip():
    response = add_destination(BODY)

    body = response.json()

    assert response.status_code == 201
    assert body["position"] == 1
    assert body["trip_id"] == str(TRIP.id)
    assert body["category"] == "beach"
    assert body["photo_url"] == "http://img/x.png"


def test_add_without_optional_fields_returns_null_photo():
    body = {key: value for key, value in BODY.items() if key not in ("photo_url", "description")}

    response = add_destination(body)

    assert response.status_code == 201
    assert response.json()["photo_url"] is None


def test_add_with_unknown_category_returns_422():
    assert add_destination({**BODY, "category": "space"}).status_code == 422


def test_add_with_departure_before_arrival_returns_400():
    response = add_destination({**BODY, "departure_date": "2026-11-01"})

    assert response.status_code == 400
    assert response.json()["error"] == "bad_request"


def test_add_to_an_unknown_trip_returns_404():
    assert add_destination(BODY, trip_id=uuid4()).status_code == 404


def test_add_without_authentication_returns_401():
    response = TestClient(app).post(f"/api/v1/trips/{TRIP.id}/destinations", json=BODY)

    assert response.status_code == 401


def test_list_returns_an_ordered_page():
    items = [make_destination(2, "B"), make_destination(1, "A"), make_destination(3, "C")]

    response = list_destinations(items, "?limit=2")

    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 3
    assert [item["name"] for item in body["items"]] == ["A", "B"]


def test_list_with_invalid_pagination_returns_422():
    assert list_destinations(query="?offset=-1").status_code == 422


def test_update_returns_the_updated_destination():
    destination = make_destination()

    response = update_destination(destination.id, BODY, [destination])

    assert response.status_code == 200
    assert response.json()["name"] == "Floripa"
    assert response.json()["position"] == 1


def test_update_unknown_destination_returns_404():
    response = update_destination(uuid4(), BODY)

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"


def test_update_with_invalid_dates_returns_400():
    destination = make_destination()

    response = update_destination(
        destination.id, {**BODY, "departure_date": "2026-11-01"}, [destination]
    )

    assert response.status_code == 400


def test_delete_returns_204():
    destination = make_destination()

    response = delete_destination(destination.id, [destination])

    assert response.status_code == 204
    assert response.content == b""


def test_delete_unknown_destination_returns_404():
    assert delete_destination(uuid4()).status_code == 404


def test_reorder_returns_204():
    first, second = make_destination(1, "A"), make_destination(2, "B")

    response = reorder([second.id, first.id], [first, second])

    assert response.status_code == 204


def test_reorder_with_mismatching_ids_returns_400():
    first = make_destination(1, "A")

    response = reorder([first.id, uuid4()], [first])

    assert response.status_code == 400
    assert response.json()["error"] == "bad_request"


def test_reorder_with_invalid_ids_returns_422():
    response = call(
        "PUT",
        "/order",
        get_reorder_destinations_use_case,
        ReorderDestinationsUseCase,
        json={"destination_ids": ["nope"]},
    )

    assert response.status_code == 422
