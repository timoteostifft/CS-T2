from uuid import uuid4

import pytest

from recomendacoes_api.application.use_cases import SubmitReviewUseCase
from recomendacoes_api.domain.entities import Place
from recomendacoes_api.domain.exceptions import InvalidReviewError, PlaceNotFoundError
from tests.adapters.database.mock_place_repository import MockPlaceRepository
from tests.adapters.database.mock_review_repository import MockReviewRepository


def build_place(archived: bool = False) -> Place:
    return Place(
        name="Praia do Rosa",
        category="beach",
        city_id=4207304,
        cost=30.0,
        archived=archived,
    )


def test_submit_review_saves_review_and_recalculates_place_rating():
    place = build_place()
    places = MockPlaceRepository([place])
    reviews = MockReviewRepository()
    use_case = SubmitReviewUseCase(places, reviews)

    first = use_case.execute(
        place_id=place.id, device_id="device-1", rating=4, comment="Nice beach"
    )
    second = use_case.execute(place_id=place.id, device_id="device-2", rating=5)
    updated_place = places.find_by_id(place.id)

    assert first.rating == 4
    assert first.comment == "Nice beach"
    assert second.rating == 5
    assert second.comment is None
    assert updated_place.review_count == 2
    assert updated_place.average_rating == 4.5


def test_submit_review_from_same_device_replaces_previous_review():
    place = build_place()
    places = MockPlaceRepository([place])
    reviews = MockReviewRepository()
    use_case = SubmitReviewUseCase(places, reviews)

    first = use_case.execute(place_id=place.id, device_id="device-1", rating=2, comment="Bad")
    replaced = use_case.execute(place_id=place.id, device_id="device-1", rating=5, comment="Great")
    updated_place = places.find_by_id(place.id)

    assert replaced.id == first.id
    assert replaced.rating == 5
    assert replaced.comment == "Great"
    assert len(reviews.list_by_place(place.id)) == 1
    assert updated_place.review_count == 1
    assert updated_place.average_rating == 5.0


def test_submit_review_for_missing_place_raises_not_found():
    reviews = MockReviewRepository()
    use_case = SubmitReviewUseCase(MockPlaceRepository(), reviews)
    missing_id = uuid4()

    with pytest.raises(PlaceNotFoundError):
        use_case.execute(place_id=missing_id, device_id="device-1", rating=5)

    assert reviews.list_by_place(missing_id) == []


def test_submit_review_for_archived_place_raises_not_found():
    place = build_place(archived=True)
    reviews = MockReviewRepository()
    use_case = SubmitReviewUseCase(MockPlaceRepository([place]), reviews)

    with pytest.raises(PlaceNotFoundError):
        use_case.execute(place_id=place.id, device_id="device-1", rating=5)

    assert reviews.list_by_place(place.id) == []


def test_submit_review_with_invalid_rating_raises_invalid_review_error():
    place = build_place()
    reviews = MockReviewRepository()
    use_case = SubmitReviewUseCase(MockPlaceRepository([place]), reviews)

    with pytest.raises(InvalidReviewError):
        use_case.execute(place_id=place.id, device_id="device-1", rating=6)

    assert reviews.list_by_place(place.id) == []
