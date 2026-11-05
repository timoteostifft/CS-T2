from datetime import date
from uuid import uuid4

import pytest

from recomendacoes_api.application.use_cases import (
    CreateTripUseCase,
    DeleteTripUseCase,
    GetTripUseCase,
    ListTripsUseCase,
    UpdateTripUseCase,
)
from recomendacoes_api.domain.entities import Trip
from recomendacoes_api.domain.exceptions import (
    InvalidTripError,
    TripAccessDeniedError,
    TripNotFoundError,
)
from tests.adapters.database.mock_trip_repository import MockTripRepository

START = date(2026, 12, 1)
END = date(2026, 12, 10)


def make_trip(owner_id, name="Beach trip") -> Trip:
    return Trip.create(name, "Sun", START, END, owner_id)


def test_create_saves_a_trip_owned_by_the_user():
    repository = MockTripRepository()
    owner_id = uuid4()

    trip = CreateTripUseCase(repository).execute(owner_id, "Beach trip", "Sun", START, END)

    assert repository.trips == [trip]
    assert trip.owner_id == owner_id


def test_create_rejects_an_invalid_trip():
    repository = MockTripRepository()

    with pytest.raises(InvalidTripError):
        CreateTripUseCase(repository).execute(uuid4(), "Trip", "", END, START)

    assert repository.trips == []


def test_list_returns_only_the_trips_of_the_user_with_total():
    owner_id = uuid4()
    mine = [make_trip(owner_id, "A"), make_trip(owner_id, "B"), make_trip(owner_id, "C")]
    repository = MockTripRepository([*mine, make_trip(uuid4())])

    page = ListTripsUseCase(repository).execute(owner_id, limit=2, offset=1)

    assert page.items == mine[1:3]
    assert page.total == 3


def test_get_returns_the_owned_trip():
    owner_id = uuid4()
    trip = make_trip(owner_id)

    assert GetTripUseCase(MockTripRepository([trip])).execute(owner_id, trip.id) == trip


def test_get_raises_when_the_trip_does_not_exist():
    with pytest.raises(TripNotFoundError):
        GetTripUseCase(MockTripRepository()).execute(uuid4(), uuid4())


def test_get_raises_when_the_trip_belongs_to_someone_else():
    trip = make_trip(uuid4())

    with pytest.raises(TripAccessDeniedError):
        GetTripUseCase(MockTripRepository([trip])).execute(uuid4(), trip.id)


def test_update_persists_the_new_values():
    owner_id = uuid4()
    trip = make_trip(owner_id)
    repository = MockTripRepository([trip])

    updated = UpdateTripUseCase(repository).execute(
        owner_id, trip.id, "Mountain trip", "Cold", START, START
    )

    assert repository.trips == [updated]
    assert (updated.name, updated.end_date) == ("Mountain trip", START)


def test_update_rejects_invalid_data_without_persisting():
    owner_id = uuid4()
    trip = make_trip(owner_id)
    repository = MockTripRepository([trip])

    with pytest.raises(InvalidTripError):
        UpdateTripUseCase(repository).execute(owner_id, trip.id, "", "", START, END)

    assert repository.find_by_id(trip.id).name == "Beach trip"


def test_update_raises_when_the_trip_belongs_to_someone_else():
    trip = make_trip(uuid4())

    with pytest.raises(TripAccessDeniedError):
        UpdateTripUseCase(MockTripRepository([trip])).execute(
            uuid4(), trip.id, "Other", "", START, END
        )


def test_update_raises_when_the_trip_does_not_exist():
    with pytest.raises(TripNotFoundError):
        UpdateTripUseCase(MockTripRepository()).execute(uuid4(), uuid4(), "Other", "", START, END)


def test_delete_removes_the_owned_trip():
    owner_id = uuid4()
    trip = make_trip(owner_id)
    repository = MockTripRepository([trip])

    DeleteTripUseCase(repository).execute(owner_id, trip.id)

    assert repository.trips == []


def test_delete_raises_when_the_trip_belongs_to_someone_else():
    trip = make_trip(uuid4())
    repository = MockTripRepository([trip])

    with pytest.raises(TripAccessDeniedError):
        DeleteTripUseCase(repository).execute(uuid4(), trip.id)

    assert repository.trips == [trip]


def test_delete_raises_when_the_trip_does_not_exist():
    with pytest.raises(TripNotFoundError):
        DeleteTripUseCase(MockTripRepository()).execute(uuid4(), uuid4())
