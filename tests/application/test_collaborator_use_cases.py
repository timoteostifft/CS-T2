from datetime import date
from uuid import uuid4

import pytest

from recomendacoes_api.application.use_cases import (
    ChangeCollaboratorRoleUseCase,
    JoinTripUseCase,
    ListCollaboratorsUseCase,
    ListTripsUseCase,
    RemoveCollaboratorUseCase,
)
from recomendacoes_api.domain.entities import CollaboratorRole, Trip, TripRole, User
from recomendacoes_api.domain.exceptions import (
    AlreadyCollaboratorError,
    CollaboratorNotFoundError,
    TripAccessDeniedError,
    TripNotFoundError,
)
from tests.adapters.database.mock_trip_repository import MockTripRepository
from tests.adapters.database.mock_user_repository import MockUserRepository

OWNER_ID = uuid4()


def make_trip() -> Trip:
    return Trip.create("Trip", "", date(2026, 12, 1), date(2026, 12, 10), OWNER_ID)


def make_user(name: str = "Bia") -> User:
    return User.create(name, f"{name.lower()}@example.com", "hash")


def test_join_adds_the_user_as_viewer_and_persists():
    trip, user = make_trip(), make_user()
    repository = MockTripRepository([trip])

    joined = JoinTripUseCase(repository).execute(user.id, trip.invite_code)

    assert joined.role_of(user.id) == TripRole.VIEWER
    assert repository.find_by_id(trip.id).can_view(user.id)


def test_join_accepts_the_code_in_any_case_and_with_spaces():
    trip, user = make_trip(), make_user()

    joined = JoinTripUseCase(MockTripRepository([trip])).execute(
        user.id, f"  {trip.invite_code.lower()} "
    )

    assert joined.can_view(user.id)


def test_join_with_an_unknown_code_raises():
    with pytest.raises(TripNotFoundError):
        JoinTripUseCase(MockTripRepository([make_trip()])).execute(uuid4(), "NOPE")


def test_join_twice_raises_and_keeps_a_single_membership():
    trip, user = make_trip(), make_user()
    repository = MockTripRepository([trip])
    JoinTripUseCase(repository).execute(user.id, trip.invite_code)

    with pytest.raises(AlreadyCollaboratorError):
        JoinTripUseCase(repository).execute(user.id, trip.invite_code)

    assert len(repository.find_by_id(trip.id).collaborators) == 1


def test_owner_cannot_join_their_own_trip():
    trip = make_trip()

    with pytest.raises(AlreadyCollaboratorError):
        JoinTripUseCase(MockTripRepository([trip])).execute(OWNER_ID, trip.invite_code)


def test_shared_trips_show_up_in_the_dashboard_of_the_collaborator():
    shared, own, foreign = make_trip(), make_trip(), make_trip()
    user = make_user()
    shared.add_collaborator(user.id)
    own.owner_id = user.id
    repository = MockTripRepository([shared, own, foreign])

    page = ListTripsUseCase(repository).execute(user.id)

    assert {trip.id for trip in page.items} == {shared.id, own.id}
    assert page.total == 2


def test_list_collaborators_returns_users_with_their_roles_and_total():
    trip, first, second = make_trip(), make_user("Bia"), make_user("Caio")
    trip.add_collaborator(first.id)
    trip.add_collaborator(second.id, CollaboratorRole.EDITOR)
    use_case = ListCollaboratorsUseCase(
        MockTripRepository([trip]), MockUserRepository([first, second])
    )

    page = use_case.execute(OWNER_ID, trip.id, limit=1, offset=1)

    assert page.total == 2
    assert [(item.user.name, item.collaborator.role) for item in page.items] == [
        ("Caio", CollaboratorRole.EDITOR)
    ]


def test_a_viewer_may_list_the_collaborators():
    trip, viewer = make_trip(), make_user()
    trip.add_collaborator(viewer.id)
    use_case = ListCollaboratorsUseCase(MockTripRepository([trip]), MockUserRepository([viewer]))

    assert use_case.execute(viewer.id, trip.id).total == 1


def test_list_collaborators_is_denied_to_strangers():
    trip = make_trip()
    use_case = ListCollaboratorsUseCase(MockTripRepository([trip]), MockUserRepository())

    with pytest.raises(TripAccessDeniedError):
        use_case.execute(uuid4(), trip.id)


def test_owner_changes_the_role_of_a_collaborator():
    trip, user = make_trip(), make_user()
    trip.add_collaborator(user.id)
    repository = MockTripRepository([trip])

    details = ChangeCollaboratorRoleUseCase(repository, MockUserRepository([user])).execute(
        OWNER_ID, trip.id, user.id, CollaboratorRole.EDITOR
    )

    assert details.collaborator.role == CollaboratorRole.EDITOR
    assert details.user == user
    assert repository.find_by_id(trip.id).can_edit(user.id)


def test_change_role_of_a_non_collaborator_raises():
    trip = make_trip()
    use_case = ChangeCollaboratorRoleUseCase(MockTripRepository([trip]), MockUserRepository())

    with pytest.raises(CollaboratorNotFoundError):
        use_case.execute(OWNER_ID, trip.id, uuid4(), CollaboratorRole.EDITOR)


def test_owner_removes_a_collaborator():
    trip, user = make_trip(), make_user()
    trip.add_collaborator(user.id)
    repository = MockTripRepository([trip])

    RemoveCollaboratorUseCase(repository).execute(OWNER_ID, trip.id, user.id)

    assert not repository.find_by_id(trip.id).can_view(user.id)


def test_remove_a_non_collaborator_raises():
    trip = make_trip()

    with pytest.raises(CollaboratorNotFoundError):
        RemoveCollaboratorUseCase(MockTripRepository([trip])).execute(OWNER_ID, trip.id, uuid4())
