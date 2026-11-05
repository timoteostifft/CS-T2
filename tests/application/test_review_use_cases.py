from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from recomendacoes_api.application.use_cases import ListReviewsUseCase, SubmitReviewUseCase
from recomendacoes_api.domain.entities import Activity, ActivityCategory, Review, User
from recomendacoes_api.domain.exceptions import ActivityNotFoundError, InvalidReviewError
from tests.adapters.database.mock_activity_repository import MockActivityRepository
from tests.adapters.database.mock_review_repository import MockReviewRepository
from tests.adapters.database.mock_user_repository import MockUserRepository


def make_activity() -> Activity:
    return Activity.create("Boat tour", ActivityCategory.TOUR, "Floripa")


def make_user(name: str = "Ana") -> User:
    return User.create(name, f"{name.lower()}@example.com", "hash")


def test_submit_saves_the_review_and_updates_the_activity_rating():
    activity, user = make_activity(), make_user()
    activities, reviews = MockActivityRepository([activity]), MockReviewRepository()

    details = SubmitReviewUseCase(activities, reviews).execute(user, activity.id, 4, "Great")

    assert reviews.reviews == [details.review]
    assert details.user == user
    assert (details.review.rating, details.review.comment) == (4, "Great")
    assert (activities.find_by_id(activity.id).average_rating, activity.review_count) == (4.0, 1)


def test_average_considers_every_user():
    activity = make_activity()
    activities, reviews = MockActivityRepository([activity]), MockReviewRepository()
    use_case = SubmitReviewUseCase(activities, reviews)

    use_case.execute(make_user("Ana"), activity.id, 5)
    use_case.execute(make_user("Bia"), activity.id, 4)
    use_case.execute(make_user("Caio"), activity.id, 4)

    stored = activities.find_by_id(activity.id)

    assert (stored.average_rating, stored.review_count) == (4.33, 3)


def test_submitting_again_updates_the_same_review_instead_of_duplicating():
    activity, user = make_activity(), make_user()
    activities, reviews = MockActivityRepository([activity]), MockReviewRepository()
    use_case = SubmitReviewUseCase(activities, reviews)
    first = use_case.execute(user, activity.id, 5, "Great")

    second = use_case.execute(user, activity.id, 2, None)

    assert second.review.id == first.review.id
    assert len(reviews.reviews) == 1
    assert (reviews.reviews[0].rating, reviews.reviews[0].comment) == (2, None)
    assert (activities.find_by_id(activity.id).average_rating, activity.review_count) == (2.0, 1)


def test_submit_rejects_an_invalid_rating_without_persisting():
    activity = make_activity()
    activities, reviews = MockActivityRepository([activity]), MockReviewRepository()

    with pytest.raises(InvalidReviewError):
        SubmitReviewUseCase(activities, reviews).execute(make_user(), activity.id, 6)

    assert reviews.reviews == []
    assert activities.find_by_id(activity.id).review_count == 0


def test_submit_raises_for_an_unknown_activity():
    with pytest.raises(ActivityNotFoundError):
        SubmitReviewUseCase(MockActivityRepository(), MockReviewRepository()).execute(
            make_user(), uuid4(), 5
        )


def test_list_returns_reviews_with_their_authors_newest_first():
    activity, ana, bia = make_activity(), make_user("Ana"), make_user("Bia")
    now = datetime.now(UTC)
    old = Review(activity.id, ana.id, 5, "old", created_at=now - timedelta(days=1))
    recent = Review(activity.id, bia.id, 3, "recent", created_at=now)
    other = Review(uuid4(), ana.id, 1, "other activity")
    use_case = ListReviewsUseCase(
        MockActivityRepository([activity]),
        MockReviewRepository([old, recent, other]),
        MockUserRepository([ana, bia]),
    )

    page = use_case.execute(activity.id)

    assert [(item.review.comment, item.user.name) for item in page.items] == [
        ("recent", "Bia"),
        ("old", "Ana"),
    ]
    assert page.total == 2


def test_list_applies_limit_and_offset_but_keeps_the_total():
    activity, user = make_activity(), make_user()
    now = datetime.now(UTC)
    items = [
        Review(activity.id, user.id, 5, str(day), created_at=now - timedelta(days=day))
        for day in range(3)
    ]
    use_case = ListReviewsUseCase(
        MockActivityRepository([activity]),
        MockReviewRepository(items),
        MockUserRepository([user]),
    )

    page = use_case.execute(activity.id, limit=1, offset=1)

    assert [item.review.comment for item in page.items] == ["1"]
    assert page.total == 3


def test_list_is_empty_for_an_activity_without_reviews():
    activity = make_activity()
    use_case = ListReviewsUseCase(
        MockActivityRepository([activity]), MockReviewRepository(), MockUserRepository()
    )

    page = use_case.execute(activity.id)

    assert (page.items, page.total) == ([], 0)


def test_list_raises_for_an_unknown_activity():
    use_case = ListReviewsUseCase(
        MockActivityRepository(), MockReviewRepository(), MockUserRepository()
    )

    with pytest.raises(ActivityNotFoundError):
        use_case.execute(uuid4())
