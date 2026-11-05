from datetime import date
from uuid import uuid4

import pytest

from recomendacoes_api.application.use_cases import (
    AddDestinationUseCase,
    DeleteDestinationUseCase,
    ListDestinationsUseCase,
    ReorderDestinationsUseCase,
    UpdateDestinationUseCase,
)
from recomendacoes_api.domain.entities import Destination, DestinationCategory, Trip
from recomendacoes_api.domain.exceptions import (
    DestinationNotFoundError,
    InvalidDestinationError,
    TripAccessDeniedError,
    TripNotFoundError,
)
from tests.adapters.database.mock_destination_repository import MockDestinationRepository
from tests.adapters.database.mock_trip_repository import MockTripRepository

ARRIVAL = date(2026, 12, 1)
DEPARTURE = date(2026, 12, 5)
OWNER_ID = uuid4()
TRIP = Trip.create("Trip", "", date(2026, 12, 1), date(2026, 12, 31), OWNER_ID)


def make_destination(position: int, name: str = "Place", trip: Trip = TRIP) -> Destination:
    return Destination.create(
        trip.id, name, "SC", DestinationCategory.CITY, ARRIVAL, DEPARTURE, position
    )


def add(destinations: MockDestinationRepository, user_id=OWNER_ID, trip_id=TRIP.id, name="New"):
    use_case = AddDestinationUseCase(MockTripRepository([TRIP]), destinations)

    return use_case.execute(
        user_id, trip_id, name, "SC", DestinationCategory.BEACH, ARRIVAL, DEPARTURE, None, "d"
    )


def test_add_appends_the_destination_at_the_end():
    destinations = MockDestinationRepository([make_destination(1), make_destination(2)])

    created = add(destinations)

    assert created.position == 3
    assert destinations.find_by_id(created.id) == created


def test_add_starts_at_position_one_on_an_empty_trip():
    assert add(MockDestinationRepository()).position == 1


def test_add_rejects_an_invalid_destination():
    destinations = MockDestinationRepository()

    with pytest.raises(InvalidDestinationError):
        add(destinations, name=" ")

    assert destinations.destinations == []


def test_add_raises_for_an_unknown_trip():
    with pytest.raises(TripNotFoundError):
        add(MockDestinationRepository(), trip_id=uuid4())


def test_add_raises_for_a_trip_of_another_user():
    with pytest.raises(TripAccessDeniedError):
        add(MockDestinationRepository(), user_id=uuid4())


def test_list_returns_ordered_page_with_total():
    items = [make_destination(index, str(index)) for index in (3, 1, 2)]
    use_case = ListDestinationsUseCase(MockTripRepository([TRIP]), MockDestinationRepository(items))

    page = use_case.execute(OWNER_ID, TRIP.id, limit=2, offset=0)

    assert [item.position for item in page.items] == [1, 2]
    assert page.total == 3


def test_list_raises_for_a_trip_of_another_user():
    use_case = ListDestinationsUseCase(MockTripRepository([TRIP]), MockDestinationRepository())

    with pytest.raises(TripAccessDeniedError):
        use_case.execute(uuid4(), TRIP.id)


def test_update_persists_new_values():
    destination = make_destination(1)
    destinations = MockDestinationRepository([destination])
    use_case = UpdateDestinationUseCase(MockTripRepository([TRIP]), destinations)

    updated = use_case.execute(
        OWNER_ID,
        TRIP.id,
        destination.id,
        "Gramado",
        "RS",
        DestinationCategory.NATURE,
        ARRIVAL,
        DEPARTURE,
    )

    assert destinations.find_by_id(destination.id) == updated
    assert updated.name == "Gramado"


def test_update_raises_for_a_destination_of_another_trip():
    other_trip = Trip.create("Other", "", ARRIVAL, DEPARTURE, OWNER_ID)
    destination = make_destination(1, trip=other_trip)
    use_case = UpdateDestinationUseCase(
        MockTripRepository([TRIP, other_trip]), MockDestinationRepository([destination])
    )

    with pytest.raises(DestinationNotFoundError):
        use_case.execute(
            OWNER_ID, TRIP.id, destination.id, "X", "Y", DestinationCategory.CITY, ARRIVAL, ARRIVAL
        )


def test_update_raises_for_an_unknown_destination():
    use_case = UpdateDestinationUseCase(MockTripRepository([TRIP]), MockDestinationRepository())

    with pytest.raises(DestinationNotFoundError):
        use_case.execute(
            OWNER_ID, TRIP.id, uuid4(), "X", "Y", DestinationCategory.CITY, ARRIVAL, ARRIVAL
        )


def test_delete_removes_the_destination_and_closes_the_gap():
    first, second, third = (make_destination(index, str(index)) for index in (1, 2, 3))
    destinations = MockDestinationRepository([first, second, third])
    use_case = DeleteDestinationUseCase(MockTripRepository([TRIP]), destinations)

    use_case.execute(OWNER_ID, TRIP.id, second.id)

    remaining = destinations.list_by_trip(TRIP.id)

    assert [(item.name, item.position) for item in remaining] == [("1", 1), ("3", 2)]


def test_delete_raises_for_an_unknown_destination():
    use_case = DeleteDestinationUseCase(MockTripRepository([TRIP]), MockDestinationRepository())

    with pytest.raises(DestinationNotFoundError):
        use_case.execute(OWNER_ID, TRIP.id, uuid4())


def test_delete_raises_for_a_trip_of_another_user():
    destination = make_destination(1)
    use_case = DeleteDestinationUseCase(
        MockTripRepository([TRIP]), MockDestinationRepository([destination])
    )

    with pytest.raises(TripAccessDeniedError):
        use_case.execute(uuid4(), TRIP.id, destination.id)


def test_reorder_applies_the_given_order():
    first, second, third = (make_destination(index, str(index)) for index in (1, 2, 3))
    destinations = MockDestinationRepository([first, second, third])
    use_case = ReorderDestinationsUseCase(MockTripRepository([TRIP]), destinations)

    use_case.execute(OWNER_ID, TRIP.id, [third.id, first.id, second.id])

    assert [item.name for item in destinations.list_by_trip(TRIP.id)] == ["3", "1", "2"]


@pytest.mark.parametrize(
    "make_ids", [lambda ids: ids[:1], lambda ids: [*ids, uuid4()], lambda ids: [ids[0], ids[0]]]
)
def test_reorder_rejects_ids_that_do_not_match_the_trip_destinations(make_ids):
    first, second = make_destination(1, "1"), make_destination(2, "2")
    destinations = MockDestinationRepository([first, second])
    use_case = ReorderDestinationsUseCase(MockTripRepository([TRIP]), destinations)

    with pytest.raises(InvalidDestinationError):
        use_case.execute(OWNER_ID, TRIP.id, make_ids([first.id, second.id]))

    assert [item.name for item in destinations.list_by_trip(TRIP.id)] == ["1", "2"]


def test_reorder_raises_for_a_trip_of_another_user():
    use_case = ReorderDestinationsUseCase(MockTripRepository([TRIP]), MockDestinationRepository())

    with pytest.raises(TripAccessDeniedError):
        use_case.execute(uuid4(), TRIP.id, [])
