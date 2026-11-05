import pytest

from recomendacoes_api.domain.entities import Activity, ActivityCategory
from recomendacoes_api.domain.exceptions import InvalidActivityError


def make_activity(**overrides) -> Activity:
    values = {"name": "Boat tour", "category": ActivityCategory.TOUR, "location": "Floripa"}

    return Activity.create(**{**values, **overrides})


def test_create_trims_text_and_defaults_optional_fields():
    activity = make_activity(name=" Boat tour ", location=" Floripa ", description=" fun ")

    assert (activity.name, activity.location, activity.description) == (
        "Boat tour",
        "Floripa",
        "fun",
    )
    assert activity.photo_url is None


@pytest.mark.parametrize("field", ["name", "location"])
def test_blank_required_text_is_rejected(field):
    with pytest.raises(InvalidActivityError):
        make_activity(**{field: "  "})


def test_blank_photo_url_is_rejected():
    with pytest.raises(InvalidActivityError):
        make_activity(photo_url=" ")


def test_new_activity_has_no_reviews():
    activity = make_activity()

    assert activity.average_rating == 0.0
    assert activity.review_count == 0


def test_recalculate_rating_sets_average_rounded_and_count():
    activity = make_activity()

    activity.recalculate_rating([5, 4, 4])

    assert activity.average_rating == 4.33
    assert activity.review_count == 3


def test_recalculate_rating_without_ratings_resets_to_zero():
    activity = make_activity()
    activity.recalculate_rating([5])

    activity.recalculate_rating([])

    assert (activity.average_rating, activity.review_count) == (0.0, 0)


def test_activity_with_an_out_of_range_rating_or_negative_count_is_rejected():
    with pytest.raises(InvalidActivityError):
        Activity("A", ActivityCategory.TOUR, "SC", average_rating=5.5)

    with pytest.raises(InvalidActivityError):
        Activity("A", ActivityCategory.TOUR, "SC", review_count=-1)
