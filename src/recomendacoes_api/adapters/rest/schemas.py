from collections.abc import Callable
from typing import Self
from uuid import UUID

from pydantic import BaseModel, Field

from recomendacoes_api.domain.entities import City, Place, State
from recomendacoes_api.domain.pagination import DEFAULT_LIMIT, MAX_LIMIT, Page


class PaginationRequest(BaseModel):
    limit: int = Field(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT)
    offset: int = Field(0, ge=0)


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
    rating: float = Field(ge=0, le=5)
    cost: float = Field(ge=0)


class PlaceResponse(BaseModel):
    id: UUID
    name: str
    category: str
    city_id: int
    rating: float
    cost: float

    @staticmethod
    def from_entity(place: Place) -> "PlaceResponse":
        return PlaceResponse(
            id=place.id,
            name=place.name,
            category=place.category,
            city_id=place.city_id,
            rating=place.rating,
            cost=place.cost,
        )


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
