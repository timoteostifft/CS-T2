from uuid import uuid4

from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import (
    get_create_activity_use_case,
    get_current_user,
    get_get_activity_use_case,
    get_list_activities_use_case,
)
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import (
    CreateActivityUseCase,
    GetActivityUseCase,
    ListActivitiesUseCase,
)
from recomendacoes_api.domain.entities import Activity, ActivityCategory, User
from tests.adapters.database.mock_activity_repository import MockActivityRepository

USER = User.create(name="Ana", email="ana@example.com", password_hash="hash")
BODY = {
    "name": "Boat tour",
    "category": "tour",
    "location": "Floripa",
    "description": "fun",
    "photo_url": "http://img/x.png",
}


def make_activity(name: str = "Boat tour") -> Activity:
    return Activity.create(name, ActivityCategory.TOUR, "Floripa")


def create_activity(body: dict, authenticated: bool = True):
    app.dependency_overrides[get_create_activity_use_case] = lambda: CreateActivityUseCase(
        MockActivityRepository()
    )

    if authenticated:
        app.dependency_overrides[get_current_user] = lambda: USER

    response = TestClient(app).post("/api/v1/activities", json=body)

    app.dependency_overrides.clear()

    return response


def list_activities(activities=None, query: str = ""):
    app.dependency_overrides[get_list_activities_use_case] = lambda: ListActivitiesUseCase(
        MockActivityRepository(activities)
    )

    response = TestClient(app).get(f"/api/v1/activities{query}")

    app.dependency_overrides.clear()

    return response


def get_activity(activity_id, activities=None):
    app.dependency_overrides[get_get_activity_use_case] = lambda: GetActivityUseCase(
        MockActivityRepository(activities)
    )

    response = TestClient(app).get(f"/api/v1/activities/{activity_id}")

    app.dependency_overrides.clear()

    return response


def test_create_returns_201_with_the_activity():
    response = create_activity(BODY)

    body = response.json()

    assert response.status_code == 201
    assert body["name"] == "Boat tour"
    assert body["category"] == "tour"
    assert "id" in body


def test_create_without_authentication_returns_401():
    assert create_activity(BODY, authenticated=False).status_code == 401


def test_create_with_unknown_category_returns_422():
    assert create_activity({**BODY, "category": "space"}).status_code == 422


def test_create_with_blank_name_returns_400():
    response = create_activity({**BODY, "name": "   "})

    assert response.status_code == 400
    assert response.json()["error"] == "bad_request"


def test_list_is_public_and_paginated():
    items = [make_activity("B"), make_activity("A"), make_activity("C")]

    response = list_activities(items, "?limit=2")

    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 3
    assert [item["name"] for item in body["items"]] == ["A", "B"]


def test_list_with_invalid_pagination_returns_422():
    assert list_activities(query="?limit=0").status_code == 422


def test_get_is_public_and_returns_the_activity():
    activity = make_activity()

    response = get_activity(activity.id, [activity])

    assert response.status_code == 200
    assert response.json()["id"] == str(activity.id)


def test_get_unknown_activity_returns_404():
    response = get_activity(uuid4())

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"
