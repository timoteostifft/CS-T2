from uuid import uuid4

import pytest

from recomendacoes_api.application.use_cases import ListReviewsUseCase
from recomendacoes_api.domain.entities import Place, Review
from recomendacoes_api.domain.exceptions import PlaceNotFoundError
from tests.adapters.database.mock_place_repository import MockPlaceRepository
from tests.adapters.database.mock_review_repository import MockReviewRepository

PLACE = Place(name="Praia do Rosa", category="beach", city_id=4207304, cost=30.0)
ARCHIVED_PLACE = Place(
    name="Praia Fechada", category="beach", city_id=4207304, cost=0.0, archived=True
)
REVIEWS = [
    Review(place_id=PLACE.id, device_id="device-1", rating=5, comment="Amazing"),
    Review(place_id=PLACE.id, device_id="device-2", rating=3),
    Review(place_id=PLACE.id, device_id="device-3", rating=4, comment="Nice"),
    Review(place_id=uuid4(), device_id="device-1", rating=1),
]


def build_use_case() -> ListReviewsUseCase:
    return ListReviewsUseCase(
        MockPlaceRepository([PLACE, ARCHIVED_PLACE]), MockReviewRepository(REVIEWS)
    )


def test_list_reviews_returns_only_reviews_of_the_place_and_the_total():
    page = build_use_case().execute(PLACE.id)

    assert page.items == REVIEWS[:3]
    assert page.total == 3


def test_list_reviews_applies_limit_and_offset():
    page = build_use_case().execute(PLACE.id, limit=1, offset=1)

    assert page.items == [REVIEWS[1]]
    assert page.total == 3


def test_list_reviews_of_place_without_reviews_returns_empty_page():
    place = Place.create(name="Trilha Nova", category="trail", city_id=4207304, cost=0.0)
    use_case = ListReviewsUseCase(MockPlaceRepository([place]), MockReviewRepository(REVIEWS))

    page = use_case.execute(place.id)

    assert page.items == []
    assert page.total == 0


def test_list_reviews_of_missing_place_raises_not_found():
    use_case = build_use_case()
    place_id = uuid4()

    with pytest.raises(PlaceNotFoundError):
        use_case.execute(place_id)


def test_list_reviews_of_archived_place_raises_not_found():
    use_case = build_use_case()
    place_id = ARCHIVED_PLACE.id

    with pytest.raises(PlaceNotFoundError):
        use_case.execute(place_id)
