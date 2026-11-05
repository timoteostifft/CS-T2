from datetime import date
from uuid import uuid4

import pytest

from recomendacoes_api.domain.entities import Destination, DestinationCategory
from recomendacoes_api.domain.exceptions import InvalidDestinationError

ARRIVAL = date(2026, 12, 1)
DEPARTURE = date(2026, 12, 5)


def make_destination(**overrides) -> Destination:
    values = {
        "trip_id": uuid4(),
        "name": "Floripa",
        "location": "Florianópolis, SC",
        "category": DestinationCategory.BEACH,
        "arrival_date": ARRIVAL,
        "departure_date": DEPARTURE,
        "position": 1,
    }

    return Destination.create(**{**values, **overrides})


def test_create_trims_text_fields_and_defaults_optional_ones():
    destination = make_destination(name=" Floripa ", location=" SC ", description=" Sun ")

    assert (destination.name, destination.location, destination.description) == (
        "Floripa",
        "SC",
        "Sun",
    )
    assert destination.photo_url is None


def test_same_day_arrival_and_departure_is_allowed():
    assert make_destination(departure_date=ARRIVAL).departure_date == ARRIVAL


@pytest.mark.parametrize("field", ["name", "location"])
def test_blank_required_text_is_rejected(field):
    with pytest.raises(InvalidDestinationError):
        make_destination(**{field: "  "})


def test_departure_before_arrival_is_rejected():
    with pytest.raises(InvalidDestinationError):
        make_destination(departure_date=date(2026, 11, 30))


def test_position_below_one_is_rejected():
    with pytest.raises(InvalidDestinationError):
        make_destination(position=0)


def test_blank_photo_url_is_rejected():
    with pytest.raises(InvalidDestinationError):
        make_destination(photo_url="  ")


def test_update_replaces_editable_fields_and_keeps_position_and_trip():
    destination = make_destination(position=3)
    trip_id = destination.trip_id

    destination.update(
        "Gramado",
        "RS",
        DestinationCategory.NATURE,
        date(2027, 1, 1),
        date(2027, 1, 3),
        "http://img/x.png",
        "Cold",
    )

    assert (destination.name, destination.category) == ("Gramado", DestinationCategory.NATURE)
    assert destination.photo_url == "http://img/x.png"
    assert (destination.position, destination.trip_id) == (3, trip_id)


def test_update_with_invalid_data_leaves_the_destination_untouched():
    destination = make_destination()

    with pytest.raises(InvalidDestinationError):
        destination.update("", "RS", DestinationCategory.CITY, ARRIVAL, DEPARTURE, None, "")

    assert destination.name == "Floripa"


def test_move_to_changes_position_and_rejects_invalid_ones():
    destination = make_destination()

    destination.move_to(4)

    assert destination.position == 4

    with pytest.raises(InvalidDestinationError):
        destination.move_to(0)
