from datetime import date, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import (
    get_current_user,
    get_list_scheduled_activities_use_case,
    get_remove_scheduled_activity_use_case,
    get_schedule_activity_use_case,
    get_update_scheduled_activity_use_case,
)
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import (
    ListScheduledActivitiesUseCase,
    RemoveScheduledActivityUseCase,
    ScheduleActivityUseCase,
    UpdateScheduledActivityUseCase,
)
from recomendacoes_api.domain.entities import (
    Activity,
    ActivityCategory,
    Destination,
    DestinationCategory,
    ScheduledActivity,
    Trip,
    User,
)
from tests.adapters.database.mock_activity_repository import MockActivityRepository
from tests.adapters.database.mock_destination_repository import MockDestinationRepository
from tests.adapters.database.mock_scheduled_activity_repository import (
    MockScheduledActivityRepository,
)
from tests.adapters.database.mock_trip_repository import MockTripRepository

USER = User.create(name="Ana", email="ana@example.com", password_hash="hash")
TRIP = Trip.create("Trip", "", date(2026, 12, 1), date(2026, 12, 31), USER.id)
DESTINATION = Destination.create(
    TRIP.id, "Floripa", "SC", DestinationCategory.BEACH, date(2026, 12, 1), date(2026, 12, 5), 1
)
ACTIVITY = Activity.create("Boat tour", ActivityCategory.TOUR, "Floripa")
BODY = {
    "starts_at": "2026-12-02T09:00:00",
    "duration_minutes": 90,
    "planned_cost": 80.5,
    "status": "confirmed",
}


def make_scheduled(starts_at=None) -> ScheduledActivity:
    return ScheduledActivity(DESTINATION.id, ACTIVITY.id, starts_at)


def call(method: str, path: str, dependency, use_case_type, scheduled_items=None, **kwargs):
    app.dependency_overrides[get_current_user] = lambda: USER
    app.dependency_overrides[dependency] = lambda: use_case_type(
        MockTripRepository([TRIP]),
        MockDestinationRepository([DESTINATION]),
        MockActivityRepository([ACTIVITY]),
        MockScheduledActivityRepository(scheduled_items),
    )
    url = f"/api/v1/trips/{TRIP.id}/destinations/{kwargs.pop('destination_id', DESTINATION.id)}"

    response = TestClient(app).request(method, f"{url}/activities{path}", **kwargs)

    app.dependency_overrides.clear()

    return response


def schedule(body: dict, **kwargs):
    return call(
        "POST", "", get_schedule_activity_use_case, ScheduleActivityUseCase, json=body, **kwargs
    )


def list_scheduled(scheduled_items=None, query: str = ""):
    return call(
        "GET",
        query,
        get_list_scheduled_activities_use_case,
        ListScheduledActivitiesUseCase,
        scheduled_items,
    )


def update(scheduled_id, body: dict, scheduled_items=None):
    return call(
        "PUT",
        f"/{scheduled_id}",
        get_update_scheduled_activity_use_case,
        UpdateScheduledActivityUseCase,
        scheduled_items,
        json=body,
    )


def remove(scheduled_id, scheduled_items=None):
    app.dependency_overrides[get_current_user] = lambda: USER
    app.dependency_overrides[get_remove_scheduled_activity_use_case] = lambda: (
        RemoveScheduledActivityUseCase(
            MockTripRepository([TRIP]),
            MockDestinationRepository([DESTINATION]),
            MockScheduledActivityRepository(scheduled_items),
        )
    )
    url = f"/api/v1/trips/{TRIP.id}/destinations/{DESTINATION.id}/activities/{scheduled_id}"

    response = TestClient(app).delete(url)

    app.dependency_overrides.clear()

    return response


def test_schedule_returns_201_with_the_embedded_activity():
    response = schedule({**BODY, "activity_id": str(ACTIVITY.id)})

    body = response.json()

    assert response.status_code == 201
    assert body["destination_id"] == str(DESTINATION.id)
    assert body["status"] == "confirmed"
    assert body["planned_cost"] == 80.5
    assert body["starts_at"] == "2026-12-02T09:00:00"
    assert body["activity"]["name"] == "Boat tour"


def test_schedule_with_only_the_activity_uses_defaults():
    response = schedule({"activity_id": str(ACTIVITY.id)})

    body = response.json()

    assert response.status_code == 201
    assert (body["status"], body["planned_cost"], body["starts_at"]) == ("pending", 0.0, None)


def test_schedule_an_unknown_activity_returns_404():
    assert schedule({"activity_id": str(uuid4())}).status_code == 404


def test_schedule_in_an_unknown_destination_returns_404():
    response = schedule({"activity_id": str(ACTIVITY.id)}, destination_id=uuid4())

    assert response.status_code == 404


def test_schedule_with_a_timezone_returns_422():
    body = {"activity_id": str(ACTIVITY.id), "starts_at": "2026-12-02T09:00:00Z"}

    assert schedule(body).status_code == 422


def test_schedule_with_invalid_numbers_returns_422():
    assert schedule({"activity_id": str(ACTIVITY.id), "duration_minutes": 0}).status_code == 422
    assert schedule({"activity_id": str(ACTIVITY.id), "planned_cost": -1}).status_code == 422
    assert schedule({"activity_id": str(ACTIVITY.id), "status": "done"}).status_code == 422


def test_schedule_without_authentication_returns_401():
    url = f"/api/v1/trips/{TRIP.id}/destinations/{DESTINATION.id}/activities"

    assert TestClient(app).post(url, json={"activity_id": str(ACTIVITY.id)}).status_code == 401


def test_list_returns_a_chronological_page():
    late, early = make_scheduled(datetime(2026, 12, 3, 9)), make_scheduled(datetime(2026, 12, 2, 9))

    response = list_scheduled([late, early], "?limit=1")

    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 2
    assert [item["id"] for item in body["items"]] == [str(early.id)]
    assert body["items"][0]["activity"]["id"] == str(ACTIVITY.id)


def test_list_with_invalid_pagination_returns_422():
    assert list_scheduled(query="?offset=-1").status_code == 422


def test_update_returns_the_updated_item():
    item = make_scheduled()

    response = update(item.id, BODY, [item])

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"
    assert response.json()["duration_minutes"] == 90


def test_update_unknown_item_returns_404():
    response = update(uuid4(), BODY)

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"


def test_update_with_invalid_values_returns_422():
    item = make_scheduled()

    assert update(item.id, {**BODY, "duration_minutes": -5}, [item]).status_code == 422


def test_remove_returns_204():
    item = make_scheduled()

    response = remove(item.id, [item])

    assert response.status_code == 204
    assert response.content == b""


def test_remove_unknown_item_returns_404():
    assert remove(uuid4()).status_code == 404
