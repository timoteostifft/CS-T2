from datetime import date, datetime
from uuid import uuid4

import pytest

from recomendacoes_api.application.use_cases import (
    AddDestinationUseCase,
    ChangeCollaboratorRoleUseCase,
    DeleteDestinationUseCase,
    DeleteTripUseCase,
    GetTripUseCase,
    ListCollaboratorsUseCase,
    ListDestinationsUseCase,
    ListScheduledActivitiesUseCase,
    RemoveCollaboratorUseCase,
    RemoveScheduledActivityUseCase,
    ReorderDestinationsUseCase,
    ScheduleActivityUseCase,
    SetTripBudgetUseCase,
    UpdateDestinationUseCase,
    UpdateScheduledActivityUseCase,
    UpdateTripUseCase,
)
from recomendacoes_api.domain.entities import (
    Activity,
    ActivityCategory,
    ActivityStatus,
    CollaboratorRole,
    Destination,
    DestinationCategory,
    ScheduledActivity,
    Trip,
    User,
)
from recomendacoes_api.domain.exceptions import TripAccessDeniedError
from tests.adapters.database.mock_activity_repository import MockActivityRepository
from tests.adapters.database.mock_destination_repository import MockDestinationRepository
from tests.adapters.database.mock_scheduled_activity_repository import (
    MockScheduledActivityRepository,
)
from tests.adapters.database.mock_trip_repository import MockTripRepository
from tests.adapters.database.mock_user_repository import MockUserRepository

D1, D2 = date(2026, 12, 1), date(2026, 12, 10)
OWNER, EDITOR, VIEWER, STRANGER = uuid4(), uuid4(), uuid4(), uuid4()


class Context:
    def __init__(self) -> None:
        self.trip = Trip.create("Trip", "", D1, D2, OWNER)
        self.trip.add_collaborator(EDITOR, CollaboratorRole.EDITOR)
        self.trip.add_collaborator(VIEWER)
        self.destination = Destination.create(
            self.trip.id, "Floripa", "SC", DestinationCategory.BEACH, D1, D2, 1
        )
        self.activity = Activity.create("Tour", ActivityCategory.TOUR, "SC")
        self.scheduled = ScheduledActivity(self.destination.id, self.activity.id)
        self.users = [
            User("Bia", "bia@example.com", "hash", id=VIEWER),
            User("Caio", "caio@example.com", "hash", id=EDITOR),
        ]
        self.trips = MockTripRepository([self.trip])
        self.destinations = MockDestinationRepository([self.destination])
        self.activities = MockActivityRepository([self.activity])
        self.scheduled_items = MockScheduledActivityRepository([self.scheduled])

    def scheduled_use_case(self, use_case_type):
        return use_case_type(self.trips, self.destinations, self.activities, self.scheduled_items)


def get_trip(c, user):
    GetTripUseCase(c.trips).execute(user, c.trip.id)


def list_destinations(c, user):
    ListDestinationsUseCase(c.trips, c.destinations).execute(user, c.trip.id)


def list_scheduled(c, user):
    c.scheduled_use_case(ListScheduledActivitiesUseCase).execute(user, c.trip.id, c.destination.id)


def list_collaborators(c, user):
    ListCollaboratorsUseCase(c.trips, MockUserRepository(c.users)).execute(user, c.trip.id)


def set_budget(c, user):
    SetTripBudgetUseCase(c.trips).execute(user, c.trip.id, 100.0)


def add_destination(c, user):
    AddDestinationUseCase(c.trips, c.destinations).execute(
        user, c.trip.id, "New", "SC", DestinationCategory.CITY, D1, D2
    )


def update_destination(c, user):
    UpdateDestinationUseCase(c.trips, c.destinations).execute(
        user, c.trip.id, c.destination.id, "New", "SC", DestinationCategory.CITY, D1, D2
    )


def delete_destination(c, user):
    DeleteDestinationUseCase(c.trips, c.destinations).execute(user, c.trip.id, c.destination.id)


def reorder_destinations(c, user):
    ReorderDestinationsUseCase(c.trips, c.destinations).execute(user, c.trip.id, [c.destination.id])


def schedule_activity(c, user):
    c.scheduled_use_case(ScheduleActivityUseCase).execute(
        user, c.trip.id, c.destination.id, c.activity.id, datetime(2026, 12, 2, 9)
    )


def update_scheduled(c, user):
    c.scheduled_use_case(UpdateScheduledActivityUseCase).execute(
        user,
        c.trip.id,
        c.destination.id,
        c.scheduled.id,
        None,
        None,
        0.0,
        ActivityStatus.CONFIRMED,
    )


def remove_scheduled(c, user):
    RemoveScheduledActivityUseCase(c.trips, c.destinations, c.scheduled_items).execute(
        user, c.trip.id, c.destination.id, c.scheduled.id
    )


def update_trip(c, user):
    UpdateTripUseCase(c.trips).execute(user, c.trip.id, "New", "", D1, D2)


def delete_trip(c, user):
    DeleteTripUseCase(c.trips).execute(user, c.trip.id)


def change_role(c, user):
    ChangeCollaboratorRoleUseCase(c.trips, MockUserRepository(c.users)).execute(
        user, c.trip.id, VIEWER, CollaboratorRole.EDITOR
    )


def remove_collaborator(c, user):
    RemoveCollaboratorUseCase(c.trips).execute(user, c.trip.id, VIEWER)


READ_ACTIONS = [get_trip, list_destinations, list_scheduled, list_collaborators]
EDIT_ACTIONS = [
    set_budget,
    add_destination,
    update_destination,
    delete_destination,
    reorder_destinations,
    schedule_activity,
    update_scheduled,
    remove_scheduled,
]
OWNER_ACTIONS = [update_trip, delete_trip, change_role, remove_collaborator]


def ids(actions):
    return [action.__name__ for action in actions]


@pytest.mark.parametrize("user", [OWNER, EDITOR, VIEWER])
@pytest.mark.parametrize("action", READ_ACTIONS, ids=ids(READ_ACTIONS))
def test_every_participant_can_read(action, user):
    action(Context(), user)


@pytest.mark.parametrize("action", READ_ACTIONS, ids=ids(READ_ACTIONS))
def test_a_stranger_cannot_read(action):
    with pytest.raises(TripAccessDeniedError):
        action(Context(), STRANGER)


@pytest.mark.parametrize("user", [OWNER, EDITOR])
@pytest.mark.parametrize("action", EDIT_ACTIONS, ids=ids(EDIT_ACTIONS))
def test_owner_and_editor_can_edit(action, user):
    action(Context(), user)


@pytest.mark.parametrize("user", [VIEWER, STRANGER])
@pytest.mark.parametrize("action", EDIT_ACTIONS, ids=ids(EDIT_ACTIONS))
def test_viewer_and_stranger_cannot_edit(action, user):
    with pytest.raises(TripAccessDeniedError):
        action(Context(), user)


@pytest.mark.parametrize("action", OWNER_ACTIONS, ids=ids(OWNER_ACTIONS))
def test_the_owner_can_manage_the_trip_and_its_collaborators(action):
    action(Context(), OWNER)


@pytest.mark.parametrize("user", [EDITOR, VIEWER, STRANGER])
@pytest.mark.parametrize("action", OWNER_ACTIONS, ids=ids(OWNER_ACTIONS))
def test_only_the_owner_can_manage_the_trip_and_its_collaborators(action, user):
    with pytest.raises(TripAccessDeniedError):
        action(Context(), user)
