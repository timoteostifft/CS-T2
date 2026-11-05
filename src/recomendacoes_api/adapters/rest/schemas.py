from collections.abc import Callable
from datetime import date, datetime
from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, NaiveDatetime

from recomendacoes_api.domain.entities import (
    MAX_RATING,
    MIN_PASSWORD_LENGTH,
    MIN_RATING,
    Activity,
    ActivityCategory,
    ActivityStatus,
    CollaboratorDetails,
    CollaboratorRole,
    Destination,
    DestinationCategory,
    ReviewDetails,
    ScheduledActivityDetails,
    Trip,
    TripRole,
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


class BudgetRequest(BaseModel):
    amount: float = Field(ge=0)


class JoinTripRequest(BaseModel):
    code: str = Field(min_length=1)


class CollaboratorRoleRequest(BaseModel):
    role: CollaboratorRole


class CollaboratorResponse(BaseModel):
    user_id: UUID
    name: str
    email: str
    role: CollaboratorRole

    @staticmethod
    def from_entity(details: CollaboratorDetails) -> "CollaboratorResponse":
        return CollaboratorResponse(
            user_id=details.user.id,
            name=details.user.name,
            email=details.user.email,
            role=details.collaborator.role,
        )


class TripResponse(BaseModel):
    id: UUID
    name: str
    description: str
    start_date: date
    end_date: date
    budget: float | None
    owner_id: UUID
    role: TripRole
    invite_code: str | None

    @staticmethod
    def from_entity(trip: Trip, user_id: UUID) -> "TripResponse":
        return TripResponse(
            id=trip.id,
            name=trip.name,
            description=trip.description,
            start_date=trip.start_date,
            end_date=trip.end_date,
            budget=trip.budget,
            owner_id=trip.owner_id,
            role=trip.role_of(user_id),
            invite_code=trip.invite_code if trip.is_owned_by(user_id) else None,
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


class ActivityRequest(BaseModel):
    name: str = Field(min_length=1)
    category: ActivityCategory
    location: str = Field(min_length=1)
    description: str = ""
    photo_url: str | None = None


class ActivityResponse(BaseModel):
    id: UUID
    name: str
    category: ActivityCategory
    location: str
    description: str
    photo_url: str | None
    average_rating: float
    review_count: int

    @staticmethod
    def from_entity(activity: Activity) -> "ActivityResponse":
        return ActivityResponse(
            id=activity.id,
            name=activity.name,
            category=activity.category,
            location=activity.location,
            description=activity.description,
            photo_url=activity.photo_url,
            average_rating=activity.average_rating,
            review_count=activity.review_count,
        )


class ReviewRequest(BaseModel):
    rating: int = Field(ge=MIN_RATING, le=MAX_RATING)
    comment: str | None = None


class ReviewResponse(BaseModel):
    id: UUID
    activity_id: UUID
    user_id: UUID
    user_name: str
    rating: int
    comment: str | None
    created_at: datetime

    @staticmethod
    def from_entity(details: ReviewDetails) -> "ReviewResponse":
        return ReviewResponse(
            id=details.review.id,
            activity_id=details.review.activity_id,
            user_id=details.user.id,
            user_name=details.user.name,
            rating=details.review.rating,
            comment=details.review.comment,
            created_at=details.review.created_at,
        )


class ScheduledActivityDetailsRequest(BaseModel):
    starts_at: NaiveDatetime | None = None
    duration_minutes: int | None = Field(default=None, gt=0)
    planned_cost: float = Field(default=0.0, ge=0)
    status: ActivityStatus = ActivityStatus.PENDING


class ScheduleActivityRequest(ScheduledActivityDetailsRequest):
    activity_id: UUID


class ScheduledActivityResponse(BaseModel):
    id: UUID
    destination_id: UUID
    starts_at: datetime | None
    duration_minutes: int | None
    planned_cost: float
    status: ActivityStatus
    activity: ActivityResponse

    @staticmethod
    def from_entity(details: ScheduledActivityDetails) -> "ScheduledActivityResponse":
        return ScheduledActivityResponse(
            id=details.scheduled.id,
            destination_id=details.scheduled.destination_id,
            starts_at=details.scheduled.starts_at,
            duration_minutes=details.scheduled.duration_minutes,
            planned_cost=details.scheduled.planned_cost,
            status=details.scheduled.status,
            activity=ActivityResponse.from_entity(details.activity),
        )


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
