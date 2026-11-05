from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import (
    get_change_collaborator_role_use_case,
    get_current_user,
    get_list_collaborators_use_case,
    get_remove_collaborator_use_case,
)
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import (
    ChangeCollaboratorRoleUseCase,
    ListCollaboratorsUseCase,
    RemoveCollaboratorUseCase,
)
from recomendacoes_api.domain.entities import CollaboratorRole, Trip, User
from tests.adapters.database.mock_trip_repository import MockTripRepository
from tests.adapters.database.mock_user_repository import MockUserRepository

OWNER = User.create("Ana", "ana@example.com", "hash")
BIA = User.create("Bia", "bia@example.com", "hash")


def make_trip() -> Trip:
    trip = Trip.create("Trip", "", date(2026, 12, 1), date(2026, 12, 10), OWNER.id)
    trip.add_collaborator(BIA.id)

    return trip


def call(method: str, path: str, dependency, build, trip: Trip, user: User = OWNER, **kwargs):
    trips, users = MockTripRepository([trip]), MockUserRepository([OWNER, BIA])
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[dependency] = lambda: build(trips, users)

    response = TestClient(app).request(
        method, f"/api/v1/trips/{kwargs.pop('trip_id', trip.id)}/collaborators{path}", **kwargs
    )

    app.dependency_overrides.clear()

    return response


def list_collaborators(trip: Trip, user: User = OWNER, query: str = ""):
    return call(
        "GET",
        query,
        get_list_collaborators_use_case,
        ListCollaboratorsUseCase,
        trip,
        user,
    )


def change_role(trip: Trip, user_id, body: dict, user: User = OWNER):
    return call(
        "PUT",
        f"/{user_id}",
        get_change_collaborator_role_use_case,
        ChangeCollaboratorRoleUseCase,
        trip,
        user,
        json=body,
    )


def remove(trip: Trip, user_id, user: User = OWNER):
    return call(
        "DELETE",
        f"/{user_id}",
        get_remove_collaborator_use_case,
        lambda trips, users: RemoveCollaboratorUseCase(trips),
        trip,
        user,
    )


def test_list_returns_the_collaborators_with_user_data():
    response = list_collaborators(make_trip())

    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 1
    assert body["items"] == [
        {"user_id": str(BIA.id), "name": "Bia", "email": "bia@example.com", "role": "viewer"}
    ]


def test_list_is_paginated_and_validated():
    assert list_collaborators(make_trip(), query="?limit=0").status_code == 422
    assert list_collaborators(make_trip(), query="?offset=5").json()["items"] == []


def test_a_collaborator_may_list_but_a_stranger_may_not():
    trip = make_trip()

    assert list_collaborators(trip, BIA).status_code == 200
    assert list_collaborators(trip, User.create("Zed", "z@x.com", "h")).status_code == 403


def test_list_on_an_unknown_trip_returns_404():
    response = call(
        "GET",
        "",
        get_list_collaborators_use_case,
        ListCollaboratorsUseCase,
        make_trip(),
        trip_id=uuid4(),
    )

    assert response.status_code == 404


def test_owner_changes_a_role():
    trip = make_trip()

    response = change_role(trip, BIA.id, {"role": "editor"})

    assert response.status_code == 200
    assert response.json()["role"] == "editor"
    assert response.json()["user_id"] == str(BIA.id)
    assert trip.can_edit(BIA.id)


def test_change_role_with_an_invalid_role_returns_422():
    assert change_role(make_trip(), BIA.id, {"role": "owner"}).status_code == 422
    assert change_role(make_trip(), BIA.id, {}).status_code == 422


def test_change_role_of_a_non_collaborator_returns_404():
    response = change_role(make_trip(), uuid4(), {"role": "editor"})

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"


def test_only_the_owner_can_change_a_role():
    trip = make_trip()
    trip.change_collaborator_role(BIA.id, CollaboratorRole.EDITOR)

    response = change_role(trip, BIA.id, {"role": "viewer"}, user=BIA)

    assert response.status_code == 403
    assert response.json()["error"] == "forbidden"


def test_owner_removes_a_collaborator():
    trip = make_trip()

    response = remove(trip, BIA.id)

    assert response.status_code == 204
    assert response.content == b""
    assert not trip.can_view(BIA.id)


def test_remove_a_non_collaborator_returns_404():
    assert remove(make_trip(), uuid4()).status_code == 404


def test_only_the_owner_can_remove_a_collaborator():
    assert remove(make_trip(), BIA.id, user=BIA).status_code == 403
