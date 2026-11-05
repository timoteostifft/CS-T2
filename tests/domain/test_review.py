from uuid import uuid4

import pytest

from recomendacoes_api.domain.entities import Review
from recomendacoes_api.domain.exceptions import InvalidReviewError


def make_review(**overrides) -> Review:
    values = {"activity_id": uuid4(), "user_id": uuid4(), "rating": 4, "comment": "Great"}

    return Review.create(**{**values, **overrides})


@pytest.mark.parametrize("rating", [1, 2, 3, 4, 5])
def test_ratings_from_one_to_five_are_accepted(rating):
    assert make_review(rating=rating).rating == rating


@pytest.mark.parametrize("rating", [0, 6, -1])
def test_ratings_outside_one_to_five_are_rejected(rating):
    with pytest.raises(InvalidReviewError):
        make_review(rating=rating)


def test_comment_is_optional_and_trimmed():
    assert make_review(comment=None).comment is None
    assert make_review(comment="  Nice  ").comment == "Nice"


def test_blank_comment_is_stored_as_none():
    assert make_review(comment="   ").comment is None


def test_update_replaces_rating_and_comment_and_keeps_identity():
    review = make_review()
    original = (review.id, review.activity_id, review.user_id, review.created_at)

    review.update(2, "Meh")

    assert (review.rating, review.comment) == (2, "Meh")
    assert (review.id, review.activity_id, review.user_id, review.created_at) == original


def test_update_with_an_invalid_rating_leaves_the_review_untouched():
    review = make_review()

    with pytest.raises(InvalidReviewError):
        review.update(9, "x")

    assert (review.rating, review.comment) == (4, "Great")
