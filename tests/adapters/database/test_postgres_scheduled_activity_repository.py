from datetime import datetime
from uuid import uuid4

from recomendacoes_api.adapters.database.postgres_scheduled_activity_repository import (
    PostgresScheduledActivityRepository,
)
from recomendacoes_api.domain.entities import ActivityStatus, ScheduledActivity


def make_scheduled(destination_id, starts_at=None) -> ScheduledActivity:
    return ScheduledActivity(
        destination_id, uuid4(), starts_at, duration_minutes=60, planned_cost=25.5
    )


def test_save_then_find_by_id_returns_the_scheduled_activity(session_factory):
    repository = PostgresScheduledActivityRepository(session_factory)
    scheduled = make_scheduled(uuid4(), datetime(2026, 12, 2, 9))

    repository.save(scheduled)

    assert repository.find_by_id(scheduled.id) == scheduled


def test_find_by_id_returns_none_when_missing(session_factory):
    assert PostgresScheduledActivityRepository(session_factory).find_by_id(uuid4()) is None


def test_list_by_destination_is_chronological_with_unscheduled_last(session_factory):
    repository = PostgresScheduledActivityRepository(session_factory)
    destination_id = uuid4()
    unscheduled = make_scheduled(destination_id)
    late = make_scheduled(destination_id, datetime(2026, 12, 3, 9))
    early = make_scheduled(destination_id, datetime(2026, 12, 2, 9))

    for item in (unscheduled, late, early):
        repository.save(item)

    repository.save(make_scheduled(uuid4(), datetime(2026, 12, 1, 9)))

    assert repository.list_by_destination(destination_id) == [early, late, unscheduled]


def test_list_by_destination_applies_limit_and_offset(session_factory):
    repository = PostgresScheduledActivityRepository(session_factory)
    destination_id = uuid4()
    items = [make_scheduled(destination_id, datetime(2026, 12, day, 9)) for day in (2, 3, 4)]

    for item in items:
        repository.save(item)

    assert repository.list_by_destination(destination_id, limit=1, offset=1) == [items[1]]


def test_list_by_destination_is_empty_without_items(session_factory):
    assert PostgresScheduledActivityRepository(session_factory).list_by_destination(uuid4()) == []


def test_count_by_destination_only_counts_its_items(session_factory):
    repository = PostgresScheduledActivityRepository(session_factory)
    destination_id = uuid4()
    repository.save(make_scheduled(destination_id))
    repository.save(make_scheduled(destination_id))
    repository.save(make_scheduled(uuid4()))

    assert repository.count_by_destination(destination_id) == 2
    assert repository.count_by_destination(uuid4()) == 0


def test_update_persists_changes(session_factory):
    repository = PostgresScheduledActivityRepository(session_factory)
    scheduled = make_scheduled(uuid4())
    repository.save(scheduled)

    scheduled.update(datetime(2026, 12, 5, 18), None, 0.0, ActivityStatus.COMPLETED)
    repository.update(scheduled)

    assert repository.find_by_id(scheduled.id) == scheduled


def test_delete_removes_only_the_given_item(session_factory):
    repository = PostgresScheduledActivityRepository(session_factory)
    destination_id = uuid4()
    removed, kept = make_scheduled(destination_id), make_scheduled(destination_id)
    repository.save(removed)
    repository.save(kept)

    repository.delete(removed.id)

    assert repository.list_by_destination(destination_id) == [kept]
