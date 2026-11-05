from collections.abc import Callable
from datetime import date
from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from recomendacoes_api.domain.entities import (
    MIN_PASSWORD_LENGTH,
    Destination,
    DestinationCategory,
    Trip,
    User,
)
from recomendacoes_api.domain.pagination import DEFAULT_LIMIT, MAX_LIMIT, Page


class PaginationRequest(BaseModel):
    limit: int = Field(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT)
    offset: int = Field(0, ge=0)


class PageResponse[T](BaseModel):
    total: int
    items: list[T]

    @classmethod
    def from_page[E](cls, page: Page[E], to_response: Callable[[E], T]) -> Self:
        return cls(total=page.total, items=[to_response(item) for item in page.items])


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str

    @staticmethod
    def from_entity(user: User) -> "UserResponse":
        return UserResponse(id=user.id, name=user.name, email=user.email)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"

    @staticmethod
    def from_token(token: str) -> "TokenResponse":
        return TokenResponse(access_token=token)


class TripRequest(BaseModel):
    name: str = Field(min_length=1)
    description: str = ""
    start_date: date
    end_date: date


class TripResponse(BaseModel):
    id: UUID
    name: str
    description: str
    start_date: date
    end_date: date
    owner_id: UUID

    @staticmethod
    def from_entity(trip: Trip) -> "TripResponse":
        return TripResponse(
            id=trip.id,
            name=trip.name,
            description=trip.description,
            start_date=trip.start_date,
            end_date=trip.end_date,
            owner_id=trip.owner_id,
        )


class DestinationRequest(BaseModel):
    name: str = Field(min_length=1)
    location: str = Field(min_length=1)
    category: DestinationCategory
    arrival_date: date
    departure_date: date
    photo_url: str | None = None
    description: str = ""


class ReorderDestinationsRequest(BaseModel):
    destination_ids: list[UUID]


class DestinationResponse(BaseModel):
    id: UUID
    trip_id: UUID
    position: int
    name: str
    location: str
    category: DestinationCategory
    arrival_date: date
    departure_date: date
    photo_url: str | None
    description: str

    @staticmethod
    def from_entity(destination: Destination) -> "DestinationResponse":
        return DestinationResponse(
            id=destination.id,
            trip_id=destination.trip_id,
            position=destination.position,
            name=destination.name,
            location=destination.location,
            category=destination.category,
            arrival_date=destination.arrival_date,
            departure_date=destination.departure_date,
            photo_url=destination.photo_url,
            description=destination.description,
        )


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
