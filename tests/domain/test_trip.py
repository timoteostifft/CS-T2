from datetime import date
from uuid import uuid4

import pytest

from recomendacoes_api.domain.entities import Trip
from recomendacoes_api.domain.exceptions import InvalidTripError

START = date(2026, 12, 1)
END = date(2026, 12, 10)


def make_trip(**overrides) -> Trip:
    values = {
        "name": "Beach trip",
        "description": "Sun",
        "start_date": START,
        "end_date": END,
        "owner_id": uuid4(),
    }

    return Trip.create(**{**values, **overrides})


def test_create_trims_name_and_description():
    trip = make_trip(name="  Beach trip ", description="  Sun ")

    assert trip.name == "Beach trip"
    assert trip.description == "Sun"


def test_trip_may_start_and_end_on_the_same_day():
    assert make_trip(end_date=START).end_date == START


@pytest.mark.parametrize("name", ["", "   "])
def test_empty_name_is_rejected(name):
    with pytest.raises(InvalidTripError):
        make_trip(name=name)


def test_end_date_before_start_date_is_rejected():
    with pytest.raises(InvalidTripError):
        make_trip(end_date=date(2026, 11, 30))


def test_is_owned_by_only_matches_the_owner():
    trip = make_trip()

    assert trip.is_owned_by(trip.owner_id) is True
    assert trip.is_owned_by(uuid4()) is False


def test_update_replaces_the_editable_fields_and_keeps_identity():
    trip = make_trip()
    original_id, original_owner = trip.id, trip.owner_id

    trip.update("Mountain trip", "Cold", date(2027, 1, 1), date(2027, 1, 5))

    assert (trip.name, trip.description) == ("Mountain trip", "Cold")
    assert (trip.start_date, trip.end_date) == (date(2027, 1, 1), date(2027, 1, 5))
    assert (trip.id, trip.owner_id) == (original_id, original_owner)


def test_update_with_invalid_data_leaves_the_trip_untouched():
    trip = make_trip()

    with pytest.raises(InvalidTripError):
        trip.update("Other", "", END, START)

    assert (trip.name, trip.start_date, trip.end_date) == ("Beach trip", START, END)
