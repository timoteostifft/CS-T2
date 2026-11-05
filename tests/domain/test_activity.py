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
