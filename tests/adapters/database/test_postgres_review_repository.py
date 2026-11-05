from uuid import uuid4

from recomendacoes_api.adapters.database.postgres_review_repository import PostgresReviewRepository
from recomendacoes_api.domain.entities import Review


def build_review(**overrides) -> Review:
    data = {
        "place_id": uuid4(),
        "device_id": "device-1",
        "rating": 5,
        "comment": "Awesome",
    }

    return Review.create(**{**data, **overrides})


def test_save_then_find_by_place_and_device_returns_the_review(session_factory):
    repository = PostgresReviewRepository(session_factory)
    review = build_review()

    repository.save(review)

    assert repository.find_by_place_and_device(review.place_id, review.device_id) == review


def test_find_by_place_and_device_returns_none_when_missing(session_factory):
    repository = PostgresReviewRepository(session_factory)

    assert repository.find_by_place_and_device(uuid4(), "device-1") is None


def test_list_by_place_returns_only_reviews_for_the_given_place(session_factory):
    repository = PostgresReviewRepository(session_factory)
    place_id = uuid4()
    first = build_review(place_id=place_id, device_id="device-1", rating=4)
    second = build_review(place_id=place_id, device_id="device-2", rating=5)
    other = build_review(place_id=uuid4(), device_id="device-1", rating=2)

    repository.save(first)
    repository.save(second)
    repository.save(other)

    reviews = repository.list_by_place(place_id)

    assert {review.id for review in reviews} == {first.id, second.id}


def test_list_by_place_applies_limit_and_offset_in_a_stable_order(session_factory):
    repository = PostgresReviewRepository(session_factory)
    place_id = uuid4()
    reviews = [build_review(place_id=place_id, device_id=f"device-{i}") for i in range(3)]
    ordered_ids = sorted(review.id for review in reviews)

    for review in reviews:
        repository.save(review)

    page = repository.list_by_place(place_id, limit=1, offset=1)

    assert [review.id for review in page] == [ordered_ids[1]]


def test_list_by_place_returns_empty_list_when_place_has_no_reviews(session_factory):
    repository = PostgresReviewRepository(session_factory)

    assert repository.list_by_place(uuid4()) == []


def test_count_by_place_counts_only_reviews_for_the_given_place(session_factory):
    repository = PostgresReviewRepository(session_factory)
    place_id = uuid4()

    repository.save(build_review(place_id=place_id, device_id="device-1"))
    repository.save(build_review(place_id=place_id, device_id="device-2"))
    repository.save(build_review(place_id=uuid4(), device_id="device-1"))

    assert repository.count_by_place(place_id) == 2


def test_count_by_place_returns_zero_when_place_has_no_reviews(session_factory):
    repository = PostgresReviewRepository(session_factory)

    assert repository.count_by_place(uuid4()) == 0


def test_update_changes_the_stored_review(session_factory):
    repository = PostgresReviewRepository(session_factory)
    review = build_review(rating=3, comment="Old")
    repository.save(review)

    review.rating = 5
    review.comment = "New"
    repository.update(review)

    stored = repository.find_by_place_and_device(review.place_id, review.device_id)

    assert stored.rating == 5
    assert stored.comment == "New"
