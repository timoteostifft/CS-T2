from uuid import uuid4

import pytest

from recomendacoes_api.domain.entities import Review
from recomendacoes_api.domain.exceptions import InvalidReviewError


def build_review(**overrides) -> Review:
    data = {
        "place_id": uuid4(),
        "device_id": "device-1",
        "rating": 5,
        "comment": "Great place",
    }

    return Review.create(**{**data, **overrides})


def test_create_review():
    place_id = uuid4()

    review = Review.create(place_id=place_id, device_id="device-1", rating=5, comment="Great place")

    assert review.place_id == place_id
    assert review.device_id == "device-1"
    assert review.rating == 5
    assert review.comment == "Great place"
    assert review.id is not None


def test_create_review_without_comment_sets_none():
    review = Review.create(place_id=uuid4(), device_id="device-1", rating=4)

    assert review.comment is None


def test_create_review_generates_distinct_ids():
    first = build_review()
    second = build_review()

    assert first.id != second.id


def test_create_review_with_blank_device_id_raises_invalid_review_error():
    with pytest.raises(InvalidReviewError):
        build_review(device_id="  ")


@pytest.mark.parametrize("rating", [0, 6, -1])
def test_create_review_with_rating_out_of_range_raises_invalid_review_error(rating):
    with pytest.raises(InvalidReviewError):
        build_review(rating=rating)


@pytest.mark.parametrize("rating", [1, 5])
def test_create_review_accepts_rating_bounds(rating):
    assert build_review(rating=rating).rating == rating
