from uuid import UUID

from recomendacoes_api.domain.entities import (
    PLACE_SORT_FIELDS,
    City,
    Place,
    Review,
    State,
)
from recomendacoes_api.domain.exceptions import InvalidPlaceError, PlaceNotFoundError
from recomendacoes_api.domain.pagination import DEFAULT_LIMIT, Page
from recomendacoes_api.ports.repositories import (
    CityRepository,
    PlaceRepository,
    ReviewRepository,
    StateRepository,
)


class GetPlaceUseCase:
    def __init__(self, place_repository: PlaceRepository) -> None:
        self._place_repository = place_repository

    def execute(self, place_id: UUID) -> Place:
        place = self._place_repository.find_by_id(place_id)

        if place is None or place.archived:
            raise PlaceNotFoundError(f"Place {place_id} not found")

        return place


class ListPlacesUseCase:
    def __init__(self, place_repository: PlaceRepository) -> None:
        self._place_repository = place_repository

    def execute(
        self,
        category: str | None = None,
        city_id: int | None = None,
        min_rating: float | None = None,
        max_cost: float | None = None,
        sort: str = "name",
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> Page[Place]:
        if sort not in PLACE_SORT_FIELDS:
            raise InvalidPlaceError(f"Invalid sort field: {sort}")

        items = self._place_repository.list_all(
            category=category,
            city_id=city_id,
            min_rating=min_rating,
            max_cost=max_cost,
            sort=sort,
            limit=limit,
            offset=offset,
        )
        total = self._place_repository.count_all(
            category=category,
            city_id=city_id,
            min_rating=min_rating,
            max_cost=max_cost,
        )

        return Page(items=items, total=total)


class CreatePlaceUseCase:
    def __init__(self, place_repository: PlaceRepository, city_repository: CityRepository) -> None:
        self._place_repository = place_repository
        self._city_repository = city_repository

    def execute(self, name: str, category: str, city_id: int, cost: float) -> Place:
        place = Place.create(name=name, category=category, city_id=city_id, cost=cost)

        if not self._city_repository.exists_by_id(city_id):
            raise InvalidPlaceError(f"City {city_id} does not exist")

        self._place_repository.save(place)

        return place


class SubmitReviewUseCase:
    def __init__(
        self, place_repository: PlaceRepository, review_repository: ReviewRepository
    ) -> None:
        self._place_repository = place_repository
        self._review_repository = review_repository

    def execute(
        self,
        place_id: UUID,
        device_id: str,
        rating: int,
        comment: str | None = None,
    ) -> Review:
        review = Review.create(
            place_id=place_id, device_id=device_id, rating=rating, comment=comment
        )
        place = self._place_repository.find_by_id(place_id)

        if place is None or place.archived:
            raise PlaceNotFoundError(f"Place {place_id} not found")

        existing = self._review_repository.find_by_place_and_device(place_id, device_id)

        if existing is not None:
            review = Review(
                id=existing.id,
                place_id=place_id,
                device_id=device_id,
                rating=rating,
                comment=comment,
            )
            self._review_repository.update(review)
        else:
            self._review_repository.save(review)

        reviews = self._review_repository.list_by_place(place_id)
        place.recalculate_rating([item.rating for item in reviews])

        self._place_repository.update(place)

        return review


class ListStatesUseCase:
    def __init__(self, state_repository: StateRepository) -> None:
        self._state_repository = state_repository

    def execute(self, limit: int = DEFAULT_LIMIT, offset: int = 0) -> Page[State]:
        return Page(
            items=self._state_repository.list_all(limit, offset),
            total=self._state_repository.count_all(),
        )


class ListCitiesUseCase:
    def __init__(self, city_repository: CityRepository) -> None:
        self._city_repository = city_repository

    def execute(
        self, state_code: str | None = None, limit: int = DEFAULT_LIMIT, offset: int = 0
    ) -> Page[City]:
        code = state_code.upper() if state_code else None

        return Page(
            items=self._city_repository.list_all(code, limit, offset),
            total=self._city_repository.count_all(code),
        )
