from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import (
    get_create_trip_use_case,
    get_current_user,
    get_delete_trip_use_case,
    get_get_trip_use_case,
    get_join_trip_use_case,
    get_list_trips_use_case,
    get_set_trip_budget_use_case,
    get_update_trip_use_case,
)
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import (
    CreateTripUseCase,
    DeleteTripUseCase,
    GetTripUseCase,
    JoinTripUseCase,
    ListTripsUseCase,
    SetTripBudgetUseCase,
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


def set_budget(trip_id, body: dict, trips=None):
    return call(
        "PUT",
        f"/{trip_id}/budget",
        get_set_trip_budget_use_case,
        SetTripBudgetUseCase,
        trips,
        json=body,
    )


def test_trip_response_exposes_a_null_budget_by_default():
    response = create_trip(BODY)

    assert response.json()["budget"] is None


def test_set_budget_returns_the_trip_with_the_budget():
    trip = make_trip()

    response = set_budget(trip.id, {"amount": 4200.5}, [trip])

    assert response.status_code == 200
    assert response.json()["budget"] == 4200.5
    assert response.json()["id"] == str(trip.id)


def test_set_budget_accepts_zero():
    trip = make_trip()

    assert set_budget(trip.id, {"amount": 0}, [trip]).json()["budget"] == 0


def test_set_budget_with_a_negative_amount_returns_422():
    trip = make_trip()

    assert set_budget(trip.id, {"amount": -1}, [trip]).status_code == 422


def test_set_budget_without_an_amount_returns_422():
    trip = make_trip()

    assert set_budget(trip.id, {}, [trip]).status_code == 422


def test_set_budget_of_another_user_returns_403():
    trip = make_trip(User.create("Bia", "b@x.com", "h"))

    assert set_budget(trip.id, {"amount": 10}, [trip]).status_code == 403


def test_set_budget_on_an_unknown_trip_returns_404():
    assert set_budget(uuid4(), {"amount": 10}).status_code == 404


def as_user(user: User, method: str, path: str, dependency, use_case_type, trips, **kwargs):
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[dependency] = lambda: use_case_type(MockTripRepository(trips))

    response = TestClient(app).request(method, f"/api/v1/trips{path}", **kwargs)

    app.dependency_overrides.clear()

    return response


def test_owner_sees_the_role_and_the_invite_code():
    trip = make_trip()

    body = get_trip(trip.id, [trip]).json()

    assert body["role"] == "owner"
    assert body["invite_code"] == trip.invite_code


def test_collaborators_see_their_role_but_never_the_invite_code():
    trip = make_trip()
    viewer = User.create("Bia", "b@x.com", "h")
    trip.add_collaborator(viewer.id)

    body = as_user(
        viewer, "GET", f"/{trip.id}", get_get_trip_use_case, GetTripUseCase, [trip]
    ).json()

    assert body["role"] == "viewer"
    assert body["invite_code"] is None


def test_join_returns_201_with_the_viewer_role():
    trip = make_trip()
    joiner = User.create("Bia", "b@x.com", "h")

    response = as_user(
        joiner,
        "POST",
        "/join",
        get_join_trip_use_case,
        JoinTripUseCase,
        [trip],
        json={"code": trip.invite_code},
    )

    assert response.status_code == 201
    assert response.json()["id"] == str(trip.id)
    assert response.json()["role"] == "viewer"
    assert response.json()["invite_code"] is None


def test_join_with_an_unknown_code_returns_404():
    joiner = User.create("Bia", "b@x.com", "h")

    response = as_user(
        joiner, "POST", "/join", get_join_trip_use_case, JoinTripUseCase, [], json={"code": "NOPE"}
    )

    assert response.status_code == 404


def test_join_twice_returns_409():
    trip = make_trip()
    joiner = User.create("Bia", "b@x.com", "h")
    trip.add_collaborator(joiner.id)

    response = as_user(
        joiner,
        "POST",
        "/join",
        get_join_trip_use_case,
        JoinTripUseCase,
        [trip],
        json={"code": trip.invite_code},
    )

    assert response.status_code == 409
    assert response.json()["error"] == "conflict"


def test_join_without_a_code_returns_422():
    joiner = User.create("Bia", "b@x.com", "h")

    response = as_user(
        joiner, "POST", "/join", get_join_trip_use_case, JoinTripUseCase, [], json={}
    )

    assert response.status_code == 422


def test_shared_trip_appears_in_the_dashboard_of_the_collaborator():
    trip = make_trip()
    viewer = User.create("Bia", "b@x.com", "h")
    trip.add_collaborator(viewer.id)

    body = as_user(viewer, "GET", "", get_list_trips_use_case, ListTripsUseCase, [trip]).json()

    assert body["total"] == 1
    assert body["items"][0]["role"] == "viewer"
