from datetime import UTC, datetime
from uuid import uuid4

import pytest

from recomendacoes_api.domain.entities import ActivityStatus, ScheduledActivity
from recomendacoes_api.domain.exceptions import InvalidScheduledActivityError


def make_scheduled(**overrides) -> ScheduledActivity:
    values = {"destination_id": uuid4(), "activity_id": uuid4()}

    return ScheduledActivity(**{**values, **overrides})


def test_defaults_are_pending_free_and_unscheduled():
    scheduled = make_scheduled()

    assert scheduled.status == ActivityStatus.PENDING
    assert scheduled.planned_cost == 0.0
    assert scheduled.starts_at is None
    assert scheduled.duration_minutes is None


@pytest.mark.parametrize("duration", [0, -5])
def test_non_positive_duration_is_rejected(duration):
    with pytest.raises(InvalidScheduledActivityError):
        make_scheduled(duration_minutes=duration)


def test_negative_cost_is_rejected():
    with pytest.raises(InvalidScheduledActivityError):
        make_scheduled(planned_cost=-1)


def test_timezone_aware_start_is_rejected():
    with pytest.raises(InvalidScheduledActivityError):
        make_scheduled(starts_at=datetime(2026, 12, 1, 10, tzinfo=UTC))


def test_update_replaces_editable_fields_and_keeps_links():
    scheduled = make_scheduled()
    destination_id, activity_id = scheduled.destination_id, scheduled.activity_id

    scheduled.update(datetime(2026, 12, 1, 10), 90, 50.0, ActivityStatus.CONFIRMED)

    assert scheduled.starts_at == datetime(2026, 12, 1, 10)
    assert (scheduled.duration_minutes, scheduled.planned_cost) == (90, 50.0)
    assert scheduled.status == ActivityStatus.CONFIRMED
    assert (scheduled.destination_id, scheduled.activity_id) == (destination_id, activity_id)


def test_update_with_invalid_data_leaves_it_untouched():
    scheduled = make_scheduled(planned_cost=10.0)

    with pytest.raises(InvalidScheduledActivityError):
        scheduled.update(None, 0, 10.0, ActivityStatus.PENDING)

    assert scheduled.duration_minutes is None
