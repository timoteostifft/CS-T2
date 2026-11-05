from collections.abc import Callable
from datetime import datetime
from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, Field

from recomendacoes_api.domain.entities import (
    MAX_RATING,
    MIN_RATING,
    City,
    Place,
    Report,
    Review,
    State,
)
from recomendacoes_api.domain.pagination import DEFAULT_LIMIT, MAX_LIMIT, Page

PlaceSortField = Literal["name", "rating", "cost"]


class PaginationRequest(BaseModel):
    limit: int = Field(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT)
    offset: int = Field(0, ge=0)


class PlaceListRequest(PaginationRequest):
    category: str | None = None
    city_id: int | None = None
    min_rating: float | None = Field(default=None, ge=0, le=MAX_RATING)
    max_cost: float | None = Field(default=None, ge=0)
    sort: PlaceSortField = "name"


class CityListRequest(PaginationRequest):
    state_code: str | None = None


class PageResponse[T](BaseModel):
    total: int
    items: list[T]

    @classmethod
    def from_page[E](cls, page: Page[E], to_response: Callable[[E], T]) -> Self:
        return cls(total=page.total, items=[to_response(item) for item in page.items])


class PlaceRequest(BaseModel):
    name: str
    category: str
    city_id: int
    cost: float = Field(ge=0)


class PlaceResponse(BaseModel):
    id: UUID
    name: str
    category: str
    city_id: int
    cost: float
    average_rating: float
    review_count: int

    @staticmethod
    def from_entity(place: Place) -> "PlaceResponse":
        return PlaceResponse(
            id=place.id,
            name=place.name,
            category=place.category,
            city_id=place.city_id,
            cost=place.cost,
            average_rating=place.average_rating,
            review_count=place.review_count,
        )


class ReviewRequest(BaseModel):
    device_id: str
    rating: int = Field(ge=MIN_RATING, le=MAX_RATING)
    comment: str | None = None


class ReviewResponse(BaseModel):
    id: UUID
    place_id: UUID
    device_id: str
    rating: int
    comment: str | None = None

    @staticmethod
    def from_entity(review: Review) -> "ReviewResponse":
        return ReviewResponse(
            id=review.id,
            place_id=review.place_id,
            device_id=review.device_id,
            rating=review.rating,
            comment=review.comment,
        )


class ReportResponse(BaseModel):
    id: UUID
    place_id: UUID
    created_at: datetime

    @staticmethod
    def from_entity(report: Report) -> "ReportResponse":
        return ReportResponse(id=report.id, place_id=report.place_id, created_at=report.created_at)


class StateResponse(BaseModel):
    code: str
    name: str

    @staticmethod
    def from_entity(state: State) -> "StateResponse":
        return StateResponse(code=state.code, name=state.name)


class CityResponse(BaseModel):
    id: int
    name: str
    state_code: str

    @staticmethod
    def from_entity(city: City) -> "CityResponse":
        return CityResponse(id=city.id, name=city.name, state_code=city.state_code)
