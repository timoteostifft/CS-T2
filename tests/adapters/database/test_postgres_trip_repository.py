from datetime import date, timedelta
from uuid import uuid4

from recomendacoes_api.adapters.database.postgres_trip_repository import PostgresTripRepository
from recomendacoes_api.adapters.database.postgres_user_repository import PostgresUserRepository
from recomendacoes_api.domain.entities import Trip, User


def make_owner(session_factory) -> User:
    user = User.create(name="Ana", email=f"{uuid4()}@example.com", password_hash="hash")
    PostgresUserRepository(session_factory).save(user)

    return user


def make_trip(owner: User, name: str = "Trip", start: date = date(2026, 12, 1)) -> Trip:
    return Trip.create(name, "desc", start, start + timedelta(days=5), owner.id)


def test_save_then_find_by_id_returns_the_trip(session_factory):
    repository = PostgresTripRepository(session_factory)
    trip = make_trip(make_owner(session_factory))

    repository.save(trip)

    assert repository.find_by_id(trip.id) == trip


def test_find_by_id_returns_none_when_missing(session_factory):
    assert PostgresTripRepository(session_factory).find_by_id(uuid4()) is None


def test_list_by_user_returns_only_the_user_trips_ordered_by_start_date(session_factory):
    repository = PostgresTripRepository(session_factory)
    owner, other = make_owner(session_factory), make_owner(session_factory)
    late = make_trip(owner, "Late", date(2027, 3, 1))
    early = make_trip(owner, "Early", date(2026, 12, 1))
    repository.save(late)
    repository.save(early)
    repository.save(make_trip(other))

    assert repository.list_by_user(owner.id) == [early, late]


def test_list_by_user_applies_limit_and_offset(session_factory):
    repository = PostgresTripRepository(session_factory)
    owner = make_owner(session_factory)
    trips = [make_trip(owner, str(index), date(2026, 12, index + 1)) for index in range(3)]

    for trip in trips:
        repository.save(trip)

    assert repository.list_by_user(owner.id, limit=1, offset=1) == [trips[1]]


def test_list_by_user_is_empty_without_trips(session_factory):
    assert PostgresTripRepository(session_factory).list_by_user(uuid4()) == []


def test_count_by_user_ignores_limit_and_other_users(session_factory):
    repository = PostgresTripRepository(session_factory)
    owner, other = make_owner(session_factory), make_owner(session_factory)
    repository.save(make_trip(owner))
    repository.save(make_trip(owner))
    repository.save(make_trip(other))

    assert repository.count_by_user(owner.id) == 2
    assert repository.count_by_user(uuid4()) == 0


def test_update_persists_changes(session_factory):
    repository = PostgresTripRepository(session_factory)
    trip = make_trip(make_owner(session_factory))
    repository.save(trip)

    trip.update("Renamed", "new", date(2026, 12, 2), date(2026, 12, 3))
    repository.update(trip)

    assert repository.find_by_id(trip.id) == trip


def test_delete_removes_only_the_given_trip(session_factory):
    repository = PostgresTripRepository(session_factory)
    owner = make_owner(session_factory)
    removed, kept = make_trip(owner, "Removed"), make_trip(owner, "Kept")
    repository.save(removed)
    repository.save(kept)

    repository.delete(removed.id)

    assert repository.find_by_id(removed.id) is None
    assert repository.find_by_id(kept.id) == kept
