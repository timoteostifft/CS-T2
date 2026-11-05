from uuid import uuid4

import pytest

from recomendacoes_api.application.use_cases import (
    CreateActivityUseCase,
    GetActivityUseCase,
    ListActivitiesUseCase,
)
from recomendacoes_api.domain.entities import Activity, ActivityCategory
from recomendacoes_api.domain.exceptions import ActivityNotFoundError, InvalidActivityError
from tests.adapters.database.mock_activity_repository import MockActivityRepository


def make_activity(name: str = "Boat tour") -> Activity:
    return Activity.create(name, ActivityCategory.TOUR, "Floripa")


def test_create_saves_the_activity():
    repository = MockActivityRepository()

    activity = CreateActivityUseCase(repository).execute(
        "Boat tour", ActivityCategory.TOUR, "Floripa", "fun", "http://img/x.png"
    )

    assert repository.activities == [activity]
    assert activity.photo_url == "http://img/x.png"


def test_create_rejects_an_invalid_activity():
    repository = MockActivityRepository()

    with pytest.raises(InvalidActivityError):
        CreateActivityUseCase(repository).execute(" ", ActivityCategory.TOUR, "Floripa")

    assert repository.activities == []


def test_list_returns_a_page_with_the_total():
    items = [make_activity("C"), make_activity("A"), make_activity("B")]

    page = ListActivitiesUseCase(MockActivityRepository(items)).execute(limit=2, offset=0)

    assert [item.name for item in page.items] == ["A", "B"]
    assert page.total == 3


def test_get_returns_the_activity():
    activity = make_activity()

    assert GetActivityUseCase(MockActivityRepository([activity])).execute(activity.id) == activity


def test_get_raises_when_missing():
    with pytest.raises(ActivityNotFoundError):
        GetActivityUseCase(MockActivityRepository()).execute(uuid4())
