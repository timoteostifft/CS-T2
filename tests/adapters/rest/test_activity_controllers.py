from uuid import uuid4

from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import (
    get_create_activity_use_case,
    get_current_user,
    get_get_activity_use_case,
    get_list_activities_use_case,
    get_list_reviews_use_case,
    get_submit_review_use_case,
)
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import (
    CreateActivityUseCase,
    GetActivityUseCase,
    ListActivitiesUseCase,
    ListReviewsUseCase,
    SubmitReviewUseCase,
)
from recomendacoes_api.domain.entities import Activity, ActivityCategory, Review, User
from tests.adapters.database.mock_activity_repository import MockActivityRepository
from tests.adapters.database.mock_review_repository import MockReviewRepository
from tests.adapters.database.mock_user_repository import MockUserRepository

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


def submit_review(activity_id, body: dict, activities=None, authenticated: bool = True):
    repositories = MockActivityRepository(activities), MockReviewRepository()
    app.dependency_overrides[get_submit_review_use_case] = lambda: SubmitReviewUseCase(
        *repositories
    )

    if authenticated:
        app.dependency_overrides[get_current_user] = lambda: USER

    response = TestClient(app).put(f"/api/v1/activities/{activity_id}/review", json=body)

    app.dependency_overrides.clear()

    return response


def list_reviews(activity_id, activities=None, reviews=None, users=None, query: str = ""):
    app.dependency_overrides[get_list_reviews_use_case] = lambda: ListReviewsUseCase(
        MockActivityRepository(activities), MockReviewRepository(reviews), MockUserRepository(users)
    )

    response = TestClient(app).get(f"/api/v1/activities/{activity_id}/reviews{query}")

    app.dependency_overrides.clear()

    return response


def test_new_activity_exposes_zero_rating_and_count():
    body = create_activity(BODY).json()

    assert (body["average_rating"], body["review_count"]) == (0.0, 0)


def test_public_activity_page_exposes_the_rating_summary():
    activity = make_activity()
    activity.recalculate_rating([5, 4])

    body = get_activity(activity.id, [activity]).json()

    assert (body["average_rating"], body["review_count"]) == (4.5, 2)
    assert body["photo_url"] is None


def test_submit_review_returns_the_review_with_the_author():
    activity = make_activity()

    response = submit_review(activity.id, {"rating": 5, "comment": "Great"}, [activity])

    body = response.json()

    assert response.status_code == 200
    assert (body["rating"], body["comment"]) == (5, "Great")
    assert body["user_id"] == str(USER.id)
    assert body["user_name"] == "Ana"
    assert body["activity_id"] == str(activity.id)


def test_submit_review_without_comment_is_accepted():
    activity = make_activity()

    response = submit_review(activity.id, {"rating": 3}, [activity])

    assert response.status_code == 200
    assert response.json()["comment"] is None


def test_submit_review_without_authentication_returns_401():
    activity = make_activity()

    response = submit_review(activity.id, {"rating": 3}, [activity], authenticated=False)

    assert response.status_code == 401


def test_submit_review_with_a_rating_out_of_range_returns_422():
    activity = make_activity()

    assert submit_review(activity.id, {"rating": 0}, [activity]).status_code == 422
    assert submit_review(activity.id, {"rating": 6}, [activity]).status_code == 422
    assert submit_review(activity.id, {}, [activity]).status_code == 422


def test_submit_review_for_an_unknown_activity_returns_404():
    assert submit_review(uuid4(), {"rating": 4}).status_code == 404


def test_list_reviews_is_public_and_paginated():
    activity = make_activity()
    reviews = [Review(activity.id, USER.id, 5, "first"), Review(activity.id, USER.id, 3, "second")]

    response = list_reviews(activity.id, [activity], reviews, [USER], "?limit=1")

    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 2
    assert len(body["items"]) == 1
    assert body["items"][0]["user_name"] == "Ana"


def test_list_reviews_with_invalid_pagination_returns_422():
    activity = make_activity()

    assert list_reviews(activity.id, [activity], query="?limit=0").status_code == 422


def test_list_reviews_of_an_unknown_activity_returns_404():
    assert list_reviews(uuid4()).status_code == 404
