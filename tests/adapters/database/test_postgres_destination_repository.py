from datetime import date
from uuid import uuid4

from recomendacoes_api.adapters.database.postgres_destination_repository import (
    PostgresDestinationRepository,
)
from recomendacoes_api.domain.entities import Destination, DestinationCategory


def make_destination(trip_id, position: int, name: str = "Place") -> Destination:
    return Destination.create(
        trip_id,
        name,
        "SC",
        DestinationCategory.BEACH,
        date(2026, 12, 1),
        date(2026, 12, 5),
        position,
        photo_url="http://img/x.png",
        description="desc",
    )


def test_save_then_find_by_id_returns_the_destination(session_factory):
    repository = PostgresDestinationRepository(session_factory)
    destination = make_destination(uuid4(), 1)

    repository.save(destination)

    assert repository.find_by_id(destination.id) == destination


def test_find_by_id_returns_none_when_missing(session_factory):
    assert PostgresDestinationRepository(session_factory).find_by_id(uuid4()) is None


def test_list_by_trip_is_ordered_by_position_and_scoped_to_the_trip(session_factory):
    repository = PostgresDestinationRepository(session_factory)
    trip_id = uuid4()
    second, first = make_destination(trip_id, 2), make_destination(trip_id, 1)
    repository.save(second)
    repository.save(first)
    repository.save(make_destination(uuid4(), 1))

    assert repository.list_by_trip(trip_id) == [first, second]


def test_list_by_trip_applies_limit_and_offset(session_factory):
    repository = PostgresDestinationRepository(session_factory)
    trip_id = uuid4()
    items = [make_destination(trip_id, index) for index in (1, 2, 3)]

    for item in items:
        repository.save(item)

    assert repository.list_by_trip(trip_id, limit=1, offset=1) == [items[1]]


def test_list_by_trip_is_empty_without_destinations(session_factory):
    assert PostgresDestinationRepository(session_factory).list_by_trip(uuid4()) == []


def test_count_by_trip_only_counts_the_trip_destinations(session_factory):
    repository = PostgresDestinationRepository(session_factory)
    trip_id = uuid4()
    repository.save(make_destination(trip_id, 1))
    repository.save(make_destination(trip_id, 2))
    repository.save(make_destination(uuid4(), 1))

    assert repository.count_by_trip(trip_id) == 2
    assert repository.count_by_trip(uuid4()) == 0


def test_update_persists_changes(session_factory):
    repository = PostgresDestinationRepository(session_factory)
    destination = make_destination(uuid4(), 1)
    repository.save(destination)

    destination.update(
        "Gramado",
        "RS",
        DestinationCategory.NATURE,
        date(2027, 1, 1),
        date(2027, 1, 2),
        None,
        "",
    )
    repository.update(destination)

    assert repository.find_by_id(destination.id) == destination


def test_update_many_persists_every_destination(session_factory):
    repository = PostgresDestinationRepository(session_factory)
    trip_id = uuid4()
    first, second = make_destination(trip_id, 1), make_destination(trip_id, 2)
    repository.save(first)
    repository.save(second)

    first.move_to(2)
    second.move_to(1)
    repository.update_many([first, second])

    assert repository.list_by_trip(trip_id) == [second, first]


def test_delete_removes_only_the_given_destination(session_factory):
    repository = PostgresDestinationRepository(session_factory)
    trip_id = uuid4()
    removed, kept = make_destination(trip_id, 1), make_destination(trip_id, 2)
    repository.save(removed)
    repository.save(kept)

    repository.delete(removed.id)

    assert repository.list_by_trip(trip_id) == [kept]
