from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import (
    get_create_place_use_case,
    get_get_place_use_case,
    get_list_places_use_case,
    get_list_reviews_use_case,
    get_report_place_use_case,
    get_submit_review_use_case,
)
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import (
    CreatePlaceUseCase,
    GetPlaceUseCase,
    ListPlacesUseCase,
    ListReviewsUseCase,
    ReportPlaceUseCase,
    SubmitReviewUseCase,
)
from recomendacoes_api.domain.entities import City, Place, Review
from tests.adapters.database.mock_city_repository import MockCityRepository
from tests.adapters.database.mock_place_repository import MockPlaceRepository
from tests.adapters.database.mock_report_repository import MockReportRepository
from tests.adapters.database.mock_review_repository import MockReviewRepository

CITY = City(id=4207304, name="Imbituba", state_code="SC")
VALID_PLACE_BODY = {
    "name": "Praia do Rosa",
    "category": "beach",
    "city_id": CITY.id,
    "cost": 30.0,
}
VALID_REVIEW_BODY = {
    "device_id": "device-1",
    "rating": 5,
    "comment": "Amazing beach",
}


def list_places(places: list[Place], params: dict | None = None):
    use_case = ListPlacesUseCase(MockPlaceRepository(places))
    app.dependency_overrides[get_list_places_use_case] = lambda: use_case

    response = TestClient(app).get("/api/v1/places", params=params)

    app.dependency_overrides.clear()

    return response


def get_place(place_id: UUID, places: list[Place]):
    use_case = GetPlaceUseCase(MockPlaceRepository(places))
    app.dependency_overrides[get_get_place_use_case] = lambda: use_case

    response = TestClient(app).get(f"/api/v1/places/{place_id}")

    app.dependency_overrides.clear()

    return response


def create_place(body: dict, places: MockPlaceRepository | None = None):
    use_case = CreatePlaceUseCase(places or MockPlaceRepository(), MockCityRepository([CITY]))
    app.dependency_overrides[get_create_place_use_case] = lambda: use_case

    response = TestClient(app).post("/api/v1/places", json=body)

    app.dependency_overrides.clear()

    return response


def submit_review(
    place_id: UUID,
    body: dict,
    places: MockPlaceRepository | None = None,
    reviews: MockReviewRepository | None = None,
):
    use_case = SubmitReviewUseCase(
        places or MockPlaceRepository(), reviews or MockReviewRepository()
    )
    app.dependency_overrides[get_submit_review_use_case] = lambda: use_case

    response = TestClient(app).post(f"/api/v1/places/{place_id}/reviews", json=body)

    app.dependency_overrides.clear()

    return response


def list_reviews(
    place_id: UUID,
    places: list[Place],
    reviews: list[Review] | None = None,
    params: dict | None = None,
):
    use_case = ListReviewsUseCase(MockPlaceRepository(places), MockReviewRepository(reviews))
    app.dependency_overrides[get_list_reviews_use_case] = lambda: use_case

    response = TestClient(app).get(f"/api/v1/places/{place_id}/reviews", params=params)

    app.dependency_overrides.clear()

    return response


def report_place(
    place_id: UUID,
    places: MockPlaceRepository,
    reports: MockReportRepository | None = None,
    user_agent: str = "Firefox",
):
    use_case = ReportPlaceUseCase(places, reports or MockReportRepository())
    app.dependency_overrides[get_report_place_use_case] = lambda: use_case

    response = TestClient(app).post(
        f"/api/v1/places/{place_id}/reports", headers={"User-Agent": user_agent}
    )

    app.dependency_overrides.clear()

    return response


def build_places(count: int) -> list[Place]:
    return [
        Place(
            name=f"Place {i}",
            category="beach",
            city_id=CITY.id,
            cost=30.0,
            average_rating=4.5,
            review_count=2,
        )
        for i in range(count)
    ]


def test_list_places_returns_a_page_as_json():
    place = Place(
        name="Praia do Rosa",
        category="beach",
        city_id=CITY.id,
        cost=30.0,
        average_rating=4.5,
        review_count=2,
    )

    response = list_places([place])

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["name"] == "Praia do Rosa"
    assert body["items"][0]["category"] == "beach"
    assert body["items"][0]["city_id"] == CITY.id
    assert body["items"][0]["cost"] == 30.0
    assert body["items"][0]["average_rating"] == 4.5
    assert body["items"][0]["review_count"] == 2


def test_list_places_excludes_archived_places():
    active = Place.create(name="Active", category="beach", city_id=CITY.id, cost=10.0)
    archived = Place(name="Archived", category="beach", city_id=CITY.id, cost=10.0, archived=True)

    response = list_places([active, archived])

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert [item["name"] for item in response.json()["items"]] == ["Active"]


def test_list_places_filters_and_sorts():
    low = Place(
        name="B Trail",
        category="trail",
        city_id=CITY.id,
        cost=15.0,
        average_rating=4.2,
        review_count=1,
    )
    high = Place(
        name="A Trail",
        category="trail",
        city_id=CITY.id,
        cost=25.0,
        average_rating=4.8,
        review_count=3,
    )
    beach = Place(
        name="Beach",
        category="beach",
        city_id=CITY.id,
        cost=10.0,
        average_rating=5.0,
        review_count=1,
    )

    response = list_places(
        [low, high, beach],
        {
            "category": "trail",
            "city_id": CITY.id,
            "min_rating": 4.0,
            "max_cost": 30.0,
            "sort": "cost",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert [item["name"] for item in body["items"]] == ["B Trail", "A Trail"]


def test_list_places_applies_limit_and_offset():
    response = list_places(build_places(5), {"limit": 2, "offset": 3})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 5
    assert [place["name"] for place in body["items"]] == ["Place 3", "Place 4"]


def test_list_places_without_places_returns_an_empty_page():
    response = list_places([])

    assert response.status_code == 200
    assert response.json() == {"total": 0, "items": []}


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 101},
        {"offset": -1},
        {"sort": "invalid"},
        {"min_rating": -1},
        {"min_rating": 6},
        {"max_cost": -1},
    ],
)
def test_list_places_with_invalid_query_params_returns_422(params):
    assert list_places([], params).status_code == 422


def test_get_place_returns_200_with_average_rating_and_review_count():
    place = Place(
        name="Praia do Rosa",
        category="beach",
        city_id=CITY.id,
        cost=30.0,
        average_rating=4.5,
        review_count=2,
    )

    response = get_place(place.id, [place])

    assert response.status_code == 200
    assert response.json() == {
        "id": str(place.id),
        "name": "Praia do Rosa",
        "category": "beach",
        "city_id": CITY.id,
        "cost": 30.0,
        "average_rating": 4.5,
        "review_count": 2,
    }


def test_get_place_returns_404_when_missing():
    response = get_place(uuid4(), [])

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"


def test_get_place_returns_404_when_archived():
    place = Place(
        name="Praia do Rosa",
        category="beach",
        city_id=CITY.id,
        cost=30.0,
        archived=True,
    )

    response = get_place(place.id, [place])

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"


def test_create_place_returns_201_and_the_created_place_without_reviews():
    places = MockPlaceRepository()

    response = create_place(VALID_PLACE_BODY, places)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Praia do Rosa"
    assert body["category"] == "beach"
    assert body["city_id"] == CITY.id
    assert body["cost"] == 30.0
    assert body["average_rating"] == 0.0
    assert body["review_count"] == 0
    assert body["id"]
    assert places.count_all() == 1


def test_create_place_with_unknown_city_returns_400():
    response = create_place({**VALID_PLACE_BODY, "city_id": 1})

    assert response.status_code == 400
    assert response.json() == {
        "error": "bad_request",
        "code": 400,
        "message": "City 1 does not exist",
    }


def test_create_place_with_blank_name_returns_400():
    response = create_place({**VALID_PLACE_BODY, "name": " "})

    assert response.status_code == 400
    assert response.json()["error"] == "bad_request"


def test_create_place_with_negative_cost_returns_422():
    assert create_place({**VALID_PLACE_BODY, "cost": -1}).status_code == 422


def test_create_place_with_missing_field_returns_422():
    body = {key: value for key, value in VALID_PLACE_BODY.items() if key != "cost"}

    assert create_place(body).status_code == 422


def test_submit_review_returns_201_and_recalculates_place_rating():
    place = Place.create(name="Praia do Rosa", category="beach", city_id=CITY.id, cost=30.0)
    places = MockPlaceRepository([place])
    reviews = MockReviewRepository()

    response = submit_review(place.id, VALID_REVIEW_BODY, places, reviews)

    assert response.status_code == 201
    body = response.json()
    assert body["place_id"] == str(place.id)
    assert body["device_id"] == "device-1"
    assert body["rating"] == 5
    assert body["comment"] == "Amazing beach"
    assert body["id"]
    stored = places.find_by_id(place.id)
    assert stored.average_rating == 5.0
    assert stored.review_count == 1


def test_submit_review_from_same_device_replaces_previous_review():
    place = Place.create(name="Praia do Rosa", category="beach", city_id=CITY.id, cost=30.0)
    places = MockPlaceRepository([place])
    reviews = MockReviewRepository()

    submit_review(place.id, {"device_id": "device-1", "rating": 2}, places, reviews)
    response = submit_review(
        place.id, {"device_id": "device-1", "rating": 4, "comment": "Updated"}, places, reviews
    )

    assert response.status_code == 201
    stored = places.find_by_id(place.id)
    assert stored.average_rating == 4.0
    assert stored.review_count == 1


def test_submit_review_for_missing_place_returns_404():
    response = submit_review(uuid4(), VALID_REVIEW_BODY)

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"


def test_submit_review_for_archived_place_returns_404():
    place = Place(
        name="Praia do Rosa",
        category="beach",
        city_id=CITY.id,
        cost=30.0,
        archived=True,
    )
    places = MockPlaceRepository([place])

    response = submit_review(place.id, VALID_REVIEW_BODY, places)

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"


def test_submit_review_with_blank_device_id_returns_400():
    place = Place.create(name="Praia do Rosa", category="beach", city_id=CITY.id, cost=30.0)
    places = MockPlaceRepository([place])

    response = submit_review(place.id, {**VALID_REVIEW_BODY, "device_id": " "}, places)

    assert response.status_code == 400
    assert response.json()["error"] == "bad_request"


@pytest.mark.parametrize("rating", [0, 6])
def test_submit_review_with_rating_out_of_range_returns_422(rating):
    place = Place.create(name="Praia do Rosa", category="beach", city_id=CITY.id, cost=30.0)
    places = MockPlaceRepository([place])

    response = submit_review(place.id, {**VALID_REVIEW_BODY, "rating": rating}, places)

    assert response.status_code == 422


def test_list_reviews_returns_a_page_as_json():
    place = Place.create(name="Praia do Rosa", category="beach", city_id=CITY.id, cost=30.0)
    review = Review.create(place_id=place.id, device_id="device-1", rating=5, comment="Amazing")
    other = Review.create(place_id=uuid4(), device_id="device-1", rating=1)

    response = list_reviews(place.id, [place], [review, other])

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"] == [
        {
            "id": str(review.id),
            "place_id": str(place.id),
            "device_id": "device-1",
            "rating": 5,
            "comment": "Amazing",
        }
    ]


def test_list_reviews_applies_limit_and_offset():
    place = Place.create(name="Praia do Rosa", category="beach", city_id=CITY.id, cost=30.0)
    reviews = [
        Review.create(place_id=place.id, device_id=f"device-{i}", rating=4) for i in range(3)
    ]

    response = list_reviews(place.id, [place], reviews, {"limit": 1, "offset": 2})

    assert response.status_code == 200
    assert response.json()["total"] == 3
    assert [item["id"] for item in response.json()["items"]] == [str(reviews[2].id)]


def test_list_reviews_of_place_without_reviews_returns_an_empty_page():
    place = Place.create(name="Praia do Rosa", category="beach", city_id=CITY.id, cost=30.0)

    response = list_reviews(place.id, [place])

    assert response.status_code == 200
    assert response.json() == {"total": 0, "items": []}


def test_list_reviews_of_missing_place_returns_404():
    response = list_reviews(uuid4(), [])

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"
    assert response.json()["code"] == 404


def test_list_reviews_of_archived_place_returns_404():
    place = Place(name="Praia do Rosa", category="beach", city_id=CITY.id, cost=30.0, archived=True)

    response = list_reviews(place.id, [place])

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}])
def test_list_reviews_with_invalid_query_params_returns_422(params):
    place = Place.create(name="Praia do Rosa", category="beach", city_id=CITY.id, cost=30.0)

    assert list_reviews(place.id, [place], params=params).status_code == 422


def test_list_reviews_with_invalid_place_id_returns_422():
    assert list_reviews("not-a-uuid", []).status_code == 422


def test_report_place_returns_201_without_exposing_the_device_hash():
    place = Place.create(name="Praia do Rosa", category="beach", city_id=CITY.id, cost=30.0)

    response = report_place(place.id, MockPlaceRepository([place]))

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "place_id", "created_at"}
    assert body["place_id"] == str(place.id)


def test_report_place_from_same_device_returns_409():
    place = Place.create(name="Praia do Rosa", category="beach", city_id=CITY.id, cost=30.0)
    places = MockPlaceRepository([place])
    reports = MockReportRepository()

    report_place(place.id, places, reports)
    response = report_place(place.id, places, reports)

    assert response.status_code == 409
    assert response.json()["error"] == "conflict"
    assert response.json()["code"] == 409


def test_report_place_by_three_devices_archives_and_hides_the_place():
    place = Place.create(name="Praia do Rosa", category="beach", city_id=CITY.id, cost=30.0)
    places = MockPlaceRepository([place])
    reports = MockReportRepository()

    for user_agent in ["Firefox", "Chrome", "Safari"]:
        assert report_place(place.id, places, reports, user_agent).status_code == 201

    assert places.find_by_id(place.id).archived is True
    assert list_places([place]).json()["total"] == 0
    assert get_place(place.id, [place]).status_code == 404


def test_report_missing_place_returns_404():
    response = report_place(uuid4(), MockPlaceRepository())

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"


def test_report_archived_place_returns_404():
    place = Place(name="Praia do Rosa", category="beach", city_id=CITY.id, cost=30.0, archived=True)

    response = report_place(place.id, MockPlaceRepository([place]))

    assert response.status_code == 404


def test_report_place_with_invalid_place_id_returns_422():
    assert report_place("not-a-uuid", MockPlaceRepository()).status_code == 422
