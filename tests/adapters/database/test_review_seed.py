from recomendacoes_api.adapters.database.place_seed import load_places, seed_places
from recomendacoes_api.adapters.database.postgres_place_repository import PostgresPlaceRepository
from recomendacoes_api.adapters.database.postgres_review_repository import PostgresReviewRepository
from recomendacoes_api.adapters.database.review_seed import (
    MAX_REVIEWS_PER_PLACE,
    MIN_REVIEWS_PER_PLACE,
    seed_reviews,
)


def test_seed_reviews_gives_every_place_between_one_and_ten_reviews(session_factory):
    seed_places(session_factory)

    seed_reviews(session_factory)

    repository = PostgresReviewRepository(session_factory)

    for place in load_places():
        reviews = repository.list_by_place(place.id)

        assert MIN_REVIEWS_PER_PLACE <= len(reviews) <= MAX_REVIEWS_PER_PLACE


def test_seed_reviews_uses_a_distinct_device_per_review_in_each_place(session_factory):
    seed_places(session_factory)

    seed_reviews(session_factory)

    repository = PostgresReviewRepository(session_factory)

    for place in load_places():
        reviews = repository.list_by_place(place.id)

        assert len({review.device_id for review in reviews}) == len(reviews)


def test_seed_reviews_updates_the_average_rating_and_review_count_of_each_place(session_factory):
    seed_places(session_factory)

    seed_reviews(session_factory)

    places = PostgresPlaceRepository(session_factory)
    reviews = PostgresReviewRepository(session_factory)

    for seeded in load_places():
        place = places.find_by_id(seeded.id)
        ratings = [review.rating for review in reviews.list_by_place(seeded.id)]

        assert place.review_count == len(ratings)
        assert place.average_rating == sum(ratings) / len(ratings)


def test_seed_reviews_is_idempotent(session_factory):
    seed_places(session_factory)
    seed_reviews(session_factory)
    repository = PostgresReviewRepository(session_factory)
    counts = [len(repository.list_by_place(place.id)) for place in load_places()]

    seed_reviews(session_factory)

    assert [len(repository.list_by_place(place.id)) for place in load_places()] == counts


def test_seed_reviews_does_nothing_without_seeded_places(session_factory):
    seed_reviews(session_factory)

    repository = PostgresReviewRepository(session_factory)

    assert all(not repository.list_by_place(place.id) for place in load_places())
