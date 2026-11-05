from datetime import date
from uuid import uuid4

import pytest

from recomendacoes_api.domain.entities import CollaboratorRole, Trip, TripRole
from recomendacoes_api.domain.exceptions import (
    AlreadyCollaboratorError,
    CollaboratorNotFoundError,
    InvalidTripError,
)

START = date(2026, 12, 1)
END = date(2026, 12, 10)


def make_trip(**overrides) -> Trip:
    values = {
        "name": "Beach trip",
        "description": "Sun",
        "start_date": START,
        "end_date": END,
        "owner_id": uuid4(),
    }

    return Trip.create(**{**values, **overrides})


def test_create_trims_name_and_description():
    trip = make_trip(name="  Beach trip ", description="  Sun ")

    assert trip.name == "Beach trip"
    assert trip.description == "Sun"


def test_trip_may_start_and_end_on_the_same_day():
    assert make_trip(end_date=START).end_date == START


@pytest.mark.parametrize("name", ["", "   "])
def test_empty_name_is_rejected(name):
    with pytest.raises(InvalidTripError):
        make_trip(name=name)


def test_end_date_before_start_date_is_rejected():
    with pytest.raises(InvalidTripError):
        make_trip(end_date=date(2026, 11, 30))


def test_is_owned_by_only_matches_the_owner():
    trip = make_trip()

    assert trip.is_owned_by(trip.owner_id) is True
    assert trip.is_owned_by(uuid4()) is False


def test_update_replaces_the_editable_fields_and_keeps_identity():
    trip = make_trip()
    original_id, original_owner = trip.id, trip.owner_id

    trip.update("Mountain trip", "Cold", date(2027, 1, 1), date(2027, 1, 5))

    assert (trip.name, trip.description) == ("Mountain trip", "Cold")
    assert (trip.start_date, trip.end_date) == (date(2027, 1, 1), date(2027, 1, 5))
    assert (trip.id, trip.owner_id) == (original_id, original_owner)


def test_update_with_invalid_data_leaves_the_trip_untouched():
    trip = make_trip()

    with pytest.raises(InvalidTripError):
        trip.update("Other", "", END, START)

    assert (trip.name, trip.start_date, trip.end_date) == ("Beach trip", START, END)


def test_budget_is_undefined_by_default():
    assert make_trip().budget is None


def test_set_budget_stores_the_amount_including_zero():
    trip = make_trip()

    trip.set_budget(1500.5)

    assert trip.budget == 1500.5

    trip.set_budget(0)

    assert trip.budget == 0


def test_set_budget_rejects_a_negative_amount_and_keeps_the_previous_one():
    trip = make_trip()
    trip.set_budget(100)

    with pytest.raises(InvalidTripError):
        trip.set_budget(-1)

    assert trip.budget == 100


def test_trip_with_a_negative_budget_is_rejected():
    with pytest.raises(InvalidTripError):
        Trip(
            name="Trip",
            start_date=START,
            end_date=END,
            owner_id=uuid4(),
            budget=-5,
        )


def test_update_keeps_the_budget():
    trip = make_trip()
    trip.set_budget(900)

    trip.update("Other", "", START, END)

    assert trip.budget == 900


def test_each_trip_gets_its_own_uppercase_invite_code():
    first, second = make_trip(), make_trip()

    assert first.invite_code != second.invite_code
    assert first.invite_code == first.invite_code.upper()
    assert len(first.invite_code) == 8


def test_owner_has_the_owner_role_and_full_access():
    trip = make_trip()

    assert trip.role_of(trip.owner_id) == TripRole.OWNER
    assert trip.can_view(trip.owner_id) and trip.can_edit(trip.owner_id)


def test_stranger_has_no_role_and_no_access():
    trip = make_trip()
    stranger = uuid4()

    assert trip.role_of(stranger) is None
    assert not trip.can_view(stranger)
    assert not trip.can_edit(stranger)


def test_collaborator_joins_as_viewer_by_default_with_read_only_access():
    trip, user_id = make_trip(), uuid4()

    trip.add_collaborator(user_id)

    assert trip.role_of(user_id) == TripRole.VIEWER
    assert trip.can_view(user_id)
    assert not trip.can_edit(user_id)


def test_editor_can_view_and_edit_but_is_not_the_owner():
    trip, user_id = make_trip(), uuid4()

    trip.add_collaborator(user_id, CollaboratorRole.EDITOR)

    assert trip.can_view(user_id) and trip.can_edit(user_id)
    assert not trip.is_owned_by(user_id)


def test_adding_the_same_user_twice_is_rejected():
    trip, user_id = make_trip(), uuid4()
    trip.add_collaborator(user_id)

    with pytest.raises(AlreadyCollaboratorError):
        trip.add_collaborator(user_id)

    assert len(trip.collaborators) == 1


def test_owner_cannot_be_added_as_collaborator():
    trip = make_trip()

    with pytest.raises(AlreadyCollaboratorError):
        trip.add_collaborator(trip.owner_id)


def test_change_collaborator_role_updates_the_permissions():
    trip, user_id = make_trip(), uuid4()
    trip.add_collaborator(user_id)

    trip.change_collaborator_role(user_id, CollaboratorRole.EDITOR)

    assert trip.can_edit(user_id)


def test_change_role_of_a_non_collaborator_is_rejected():
    with pytest.raises(CollaboratorNotFoundError):
        make_trip().change_collaborator_role(uuid4(), CollaboratorRole.EDITOR)


def test_remove_collaborator_revokes_access():
    trip, user_id = make_trip(), uuid4()
    trip.add_collaborator(user_id)

    trip.remove_collaborator(user_id)

    assert not trip.can_view(user_id)
    assert trip.collaborators == []


def test_remove_a_non_collaborator_is_rejected():
    with pytest.raises(CollaboratorNotFoundError):
        make_trip().remove_collaborator(uuid4())
