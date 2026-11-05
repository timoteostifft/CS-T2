from datetime import date, datetime
from uuid import uuid4

import pytest

from recomendacoes_api.application.use_cases import (
    ListScheduledActivitiesUseCase,
    RemoveScheduledActivityUseCase,
    ScheduleActivityUseCase,
    UpdateScheduledActivityUseCase,
)
from recomendacoes_api.domain.entities import (
    Activity,
    ActivityCategory,
    ActivityStatus,
    Destination,
    DestinationCategory,
    ScheduledActivity,
    Trip,
)
from recomendacoes_api.domain.exceptions import (
    ActivityNotFoundError,
    DestinationNotFoundError,
    InvalidScheduledActivityError,
    ScheduledActivityNotFoundError,
    TripAccessDeniedError,
)
from tests.adapters.database.mock_activity_repository import MockActivityRepository
from tests.adapters.database.mock_destination_repository import MockDestinationRepository
from tests.adapters.database.mock_scheduled_activity_repository import (
    MockScheduledActivityRepository,
)
from tests.adapters.database.mock_trip_repository import MockTripRepository

OWNER_ID = uuid4()
TRIP = Trip.create("Trip", "", date(2026, 12, 1), date(2026, 12, 31), OWNER_ID)
DESTINATION = Destination.create(
    TRIP.id, "Floripa", "SC", DestinationCategory.BEACH, date(2026, 12, 1), date(2026, 12, 5), 1
)
ACTIVITY = Activity.create("Boat tour", ActivityCategory.TOUR, "Floripa")


def build(use_case_type, scheduled_items=None):
    scheduled = MockScheduledActivityRepository(scheduled_items)
    use_case = use_case_type(
        MockTripRepository([TRIP]),
        MockDestinationRepository([DESTINATION]),
        MockActivityRepository([ACTIVITY]),
        scheduled,
    )

    return use_case, scheduled


def make_scheduled(starts_at=None, destination_id=DESTINATION.id) -> ScheduledActivity:
    return ScheduledActivity(destination_id, ACTIVITY.id, starts_at)


def test_schedule_saves_and_returns_the_activity_details():
    use_case, scheduled = build(ScheduleActivityUseCase)

    details = use_case.execute(
        OWNER_ID,
        TRIP.id,
        DESTINATION.id,
        ACTIVITY.id,
        datetime(2026, 12, 2, 9),
        120,
        80.0,
        ActivityStatus.CONFIRMED,
    )

    assert scheduled.scheduled_items == [details.scheduled]
    assert details.activity == ACTIVITY
    assert (details.scheduled.duration_minutes, details.scheduled.planned_cost) == (120, 80.0)
    assert details.scheduled.status == ActivityStatus.CONFIRMED


def test_schedule_uses_pending_status_and_zero_cost_by_default():
    use_case, _ = build(ScheduleActivityUseCase)

    details = use_case.execute(OWNER_ID, TRIP.id, DESTINATION.id, ACTIVITY.id)

    assert details.scheduled.status == ActivityStatus.PENDING
    assert details.scheduled.planned_cost == 0.0


def test_schedule_rejects_invalid_values_without_saving():
    use_case, scheduled = build(ScheduleActivityUseCase)

    with pytest.raises(InvalidScheduledActivityError):
        use_case.execute(OWNER_ID, TRIP.id, DESTINATION.id, ACTIVITY.id, duration_minutes=0)

    assert scheduled.scheduled_items == []


def test_schedule_raises_for_an_unknown_activity():
    use_case, _ = build(ScheduleActivityUseCase)

    with pytest.raises(ActivityNotFoundError):
        use_case.execute(OWNER_ID, TRIP.id, DESTINATION.id, uuid4())


def test_schedule_raises_for_an_unknown_destination():
    use_case, _ = build(ScheduleActivityUseCase)

    with pytest.raises(DestinationNotFoundError):
        use_case.execute(OWNER_ID, TRIP.id, uuid4(), ACTIVITY.id)


def test_schedule_raises_for_a_trip_of_another_user():
    use_case, _ = build(ScheduleActivityUseCase)

    with pytest.raises(TripAccessDeniedError):
        use_case.execute(uuid4(), TRIP.id, DESTINATION.id, ACTIVITY.id)


def test_list_returns_chronological_details_with_unscheduled_last():
    late = make_scheduled(datetime(2026, 12, 3, 9))
    early = make_scheduled(datetime(2026, 12, 2, 9))
    unscheduled = make_scheduled()
    other_destination = make_scheduled(destination_id=uuid4())
    use_case, _ = build(
        ListScheduledActivitiesUseCase, [unscheduled, late, early, other_destination]
    )

    page = use_case.execute(OWNER_ID, TRIP.id, DESTINATION.id)

    assert [item.scheduled for item in page.items] == [early, late, unscheduled]
    assert all(item.activity == ACTIVITY for item in page.items)
    assert page.total == 3


def test_list_applies_limit_and_offset_but_keeps_the_total():
    items = [make_scheduled(datetime(2026, 12, day, 9)) for day in (2, 3, 4)]
    use_case, _ = build(ListScheduledActivitiesUseCase, items)

    page = use_case.execute(OWNER_ID, TRIP.id, DESTINATION.id, limit=1, offset=1)

    assert [item.scheduled for item in page.items] == [items[1]]
    assert page.total == 3


def test_list_raises_for_a_trip_of_another_user():
    use_case, _ = build(ListScheduledActivitiesUseCase)

    with pytest.raises(TripAccessDeniedError):
        use_case.execute(uuid4(), TRIP.id, DESTINATION.id)


def test_update_persists_and_returns_the_details():
    item = make_scheduled()
    use_case, scheduled = build(UpdateScheduledActivityUseCase, [item])

    details = use_case.execute(
        OWNER_ID,
        TRIP.id,
        DESTINATION.id,
        item.id,
        datetime(2026, 12, 2, 9),
        60,
        20.0,
        ActivityStatus.COMPLETED,
    )

    assert scheduled.find_by_id(item.id) == details.scheduled
    assert details.scheduled.status == ActivityStatus.COMPLETED
    assert details.activity == ACTIVITY


def test_update_rejects_invalid_values():
    item = make_scheduled()
    use_case, _ = build(UpdateScheduledActivityUseCase, [item])

    with pytest.raises(InvalidScheduledActivityError):
        use_case.execute(
            OWNER_ID, TRIP.id, DESTINATION.id, item.id, None, None, -1.0, ActivityStatus.PENDING
        )


def test_update_raises_for_an_unknown_scheduled_activity():
    use_case, _ = build(UpdateScheduledActivityUseCase)

    with pytest.raises(ScheduledActivityNotFoundError):
        use_case.execute(
            OWNER_ID, TRIP.id, DESTINATION.id, uuid4(), None, None, 0.0, ActivityStatus.PENDING
        )


def test_update_raises_for_a_scheduled_activity_of_another_destination():
    item = make_scheduled(destination_id=uuid4())
    use_case, _ = build(UpdateScheduledActivityUseCase, [item])

    with pytest.raises(ScheduledActivityNotFoundError):
        use_case.execute(
            OWNER_ID, TRIP.id, DESTINATION.id, item.id, None, None, 0.0, ActivityStatus.PENDING
        )


def remove(scheduled_items, user_id=OWNER_ID, scheduled_id=None):
    scheduled = MockScheduledActivityRepository(scheduled_items)
    use_case = RemoveScheduledActivityUseCase(
        MockTripRepository([TRIP]), MockDestinationRepository([DESTINATION]), scheduled
    )

    use_case.execute(user_id, TRIP.id, DESTINATION.id, scheduled_id or scheduled_items[0].id)

    return scheduled


def test_remove_deletes_the_scheduled_activity():
    item = make_scheduled()

    assert remove([item]).scheduled_items == []


def test_remove_raises_for_an_unknown_scheduled_activity():
    with pytest.raises(ScheduledActivityNotFoundError):
        remove([make_scheduled()], scheduled_id=uuid4())


def test_remove_raises_for_a_trip_of_another_user():
    with pytest.raises(TripAccessDeniedError):
        remove([make_scheduled()], user_id=uuid4())
