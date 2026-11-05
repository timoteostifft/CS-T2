from uuid import uuid4

from recomendacoes_api.adapters.database.postgres_activity_repository import (
    PostgresActivityRepository,
)
from recomendacoes_api.domain.entities import Activity, ActivityCategory


def make_activity(name: str = "Boat tour") -> Activity:
    return Activity.create(name, ActivityCategory.TOUR, "Floripa", "fun", "http://img/x.png")


def test_save_then_find_by_id_returns_the_activity(session_factory):
    repository = PostgresActivityRepository(session_factory)
    activity = make_activity()

    repository.save(activity)

    assert repository.find_by_id(activity.id) == activity


def test_find_by_id_returns_none_when_missing(session_factory):
    assert PostgresActivityRepository(session_factory).find_by_id(uuid4()) is None


def test_list_all_is_ordered_by_name_and_paginated(session_factory):
    repository = PostgresActivityRepository(session_factory)
    items = [make_activity(name) for name in ("C", "A", "B")]

    for item in items:
        repository.save(item)

    assert [item.name for item in repository.list_all()] == ["A", "B", "C"]
    assert [item.name for item in repository.list_all(limit=1, offset=1)] == ["B"]


def test_list_all_is_empty_without_activities(session_factory):
    assert PostgresActivityRepository(session_factory).list_all() == []


def test_count_all_returns_the_total(session_factory):
    repository = PostgresActivityRepository(session_factory)
    repository.save(make_activity("A"))
    repository.save(make_activity("B"))

    assert repository.count_all() == 2


def test_list_by_ids_returns_only_the_requested_activities(session_factory):
    repository = PostgresActivityRepository(session_factory)
    wanted, ignored = make_activity("A"), make_activity("B")
    repository.save(wanted)
    repository.save(ignored)

    assert repository.list_by_ids([wanted.id, uuid4()]) == [wanted]
    assert repository.list_by_ids([]) == []
