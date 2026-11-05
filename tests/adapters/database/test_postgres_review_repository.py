from datetime import UTC, datetime, timedelta
from uuid import uuid4

from recomendacoes_api.adapters.database.postgres_review_repository import (
    PostgresReviewRepository,
)
from recomendacoes_api.domain.entities import Review


def make_review(activity_id, user_id=None, rating=4, age_days=0) -> Review:
    return Review(
        activity_id,
        user_id or uuid4(),
        rating,
        "comment",
        created_at=datetime.now(UTC) - timedelta(days=age_days),
    )


def test_save_then_find_by_activity_and_user_returns_the_review(session_factory):
    repository = PostgresReviewRepository(session_factory)
    review = make_review(uuid4())

    repository.save(review)

    assert repository.find_by_activity_and_user(review.activity_id, review.user_id) == review


def test_find_by_activity_and_user_returns_none_when_missing(session_factory):
    repository = PostgresReviewRepository(session_factory)

    assert repository.find_by_activity_and_user(uuid4(), uuid4()) is None


def test_find_by_activity_and_user_does_not_mix_users_or_activities(session_factory):
    repository = PostgresReviewRepository(session_factory)
    review = make_review(uuid4())
    repository.save(review)

    assert repository.find_by_activity_and_user(review.activity_id, uuid4()) is None
    assert repository.find_by_activity_and_user(uuid4(), review.user_id) is None


def test_list_by_activity_is_newest_first_and_scoped_to_the_activity(session_factory):
    repository = PostgresReviewRepository(session_factory)
    activity_id = uuid4()
    old, recent = make_review(activity_id, age_days=2), make_review(activity_id, age_days=0)
    repository.save(old)
    repository.save(recent)
    repository.save(make_review(uuid4()))

    assert repository.list_by_activity(activity_id) == [recent, old]


def test_list_by_activity_applies_limit_and_offset(session_factory):
    repository = PostgresReviewRepository(session_factory)
    activity_id = uuid4()
    items = [make_review(activity_id, age_days=day) for day in range(3)]

    for item in items:
        repository.save(item)

    assert repository.list_by_activity(activity_id, limit=1, offset=1) == [items[1]]


def test_list_by_activity_is_empty_without_reviews(session_factory):
    assert PostgresReviewRepository(session_factory).list_by_activity(uuid4()) == []


def test_count_by_activity_only_counts_that_activity(session_factory):
    repository = PostgresReviewRepository(session_factory)
    activity_id = uuid4()
    repository.save(make_review(activity_id))
    repository.save(make_review(activity_id))
    repository.save(make_review(uuid4()))

    assert repository.count_by_activity(activity_id) == 2
    assert repository.count_by_activity(uuid4()) == 0


def test_list_ratings_by_activity_returns_every_rating(session_factory):
    repository = PostgresReviewRepository(session_factory)
    activity_id = uuid4()
    repository.save(make_review(activity_id, rating=5))
    repository.save(make_review(activity_id, rating=2))
    repository.save(make_review(uuid4(), rating=1))

    assert sorted(repository.list_ratings_by_activity(activity_id)) == [2, 5]
    assert repository.list_ratings_by_activity(uuid4()) == []


def test_update_persists_the_new_rating_and_comment(session_factory):
    repository = PostgresReviewRepository(session_factory)
    review = make_review(uuid4())
    repository.save(review)

    review.update(1, None)
    repository.update(review)

    stored = repository.find_by_activity_and_user(review.activity_id, review.user_id)

    assert (stored.rating, stored.comment) == (1, None)
    assert repository.count_by_activity(review.activity_id) == 1
