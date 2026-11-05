import secrets
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from recomendacoes_api.domain.exceptions import (
    AlreadyCollaboratorError,
    CollaboratorNotFoundError,
    InvalidActivityError,
    InvalidDestinationError,
    InvalidReviewError,
    InvalidScheduledActivityError,
    InvalidTripError,
    InvalidUserError,
)

MIN_PASSWORD_LENGTH = 8
FIRST_POSITION = 1
MIN_RATING = 1
MAX_RATING = 5
INVITE_CODE_BYTES = 4


class CollaboratorRole(StrEnum):
    EDITOR = "editor"
    VIEWER = "viewer"


class TripRole(StrEnum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


def generate_invite_code() -> str:
    return secrets.token_hex(INVITE_CODE_BYTES).upper()


@dataclass
class User:
    name: str
    email: str
    password_hash: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidUserError("User name must not be empty")
        if "@" not in self.email.strip("@"):
            raise InvalidUserError("User email is invalid")
        if not self.password_hash:
            raise InvalidUserError("User password hash must not be empty")

    @staticmethod
    def create(name: str, email: str, password_hash: str) -> "User":
        return User(
            name=name.strip(),
            email=User.normalize_email(email),
            password_hash=password_hash,
        )

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()


@dataclass
class Collaborator:
    user_id: UUID
    role: CollaboratorRole = CollaboratorRole.VIEWER
    id: UUID = field(default_factory=uuid4)


@dataclass
class Trip:
    name: str
    start_date: date
    end_date: date
    owner_id: UUID
    description: str = ""
    budget: float | None = None
    invite_code: str = field(default_factory=generate_invite_code)
    collaborators: list[Collaborator] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidTripError("Trip name must not be empty")
        if self.end_date < self.start_date:
            raise InvalidTripError("Trip end date must not be before its start date")
        if self.budget is not None and self.budget < 0:
            raise InvalidTripError("Trip budget must not be negative")

    @staticmethod
    def create(
        name: str, description: str, start_date: date, end_date: date, owner_id: UUID
    ) -> "Trip":
        return Trip(
            name=name.strip(),
            description=description.strip(),
            start_date=start_date,
            end_date=end_date,
            owner_id=owner_id,
        )

    def is_owned_by(self, user_id: UUID) -> bool:
        return self.owner_id == user_id

    def role_of(self, user_id: UUID) -> TripRole | None:
        if self.is_owned_by(user_id):
            return TripRole.OWNER

        collaborator = self._find_collaborator(user_id)

        return TripRole(collaborator.role.value) if collaborator else None

    def can_view(self, user_id: UUID) -> bool:
        return self.role_of(user_id) is not None

    def can_edit(self, user_id: UUID) -> bool:
        return self.role_of(user_id) in (TripRole.OWNER, TripRole.EDITOR)

    def add_collaborator(
        self, user_id: UUID, role: CollaboratorRole = CollaboratorRole.VIEWER
    ) -> Collaborator:
        if self.role_of(user_id) is not None:
            raise AlreadyCollaboratorError("User already participates in this trip")

        collaborator = Collaborator(user_id=user_id, role=role)

        self.collaborators.append(collaborator)

        return collaborator

    def change_collaborator_role(self, user_id: UUID, role: CollaboratorRole) -> Collaborator:
        collaborator = self._get_collaborator(user_id)

        collaborator.role = role

        return collaborator

    def remove_collaborator(self, user_id: UUID) -> None:
        collaborator = self._get_collaborator(user_id)

        self.collaborators.remove(collaborator)

    def _find_collaborator(self, user_id: UUID) -> Collaborator | None:
        return next((item for item in self.collaborators if item.user_id == user_id), None)

    def _get_collaborator(self, user_id: UUID) -> Collaborator:
        collaborator = self._find_collaborator(user_id)

        if collaborator is None:
            raise CollaboratorNotFoundError("User is not a collaborator of this trip")

        return collaborator

    def set_budget(self, amount: float) -> None:
        if amount < 0:
            raise InvalidTripError("Trip budget must not be negative")

        self.budget = amount

    def update(self, name: str, description: str, start_date: date, end_date: date) -> None:
        updated = Trip.create(name, description, start_date, end_date, self.owner_id)

        self.name = updated.name
        self.description = updated.description
        self.start_date = updated.start_date
        self.end_date = updated.end_date


class DestinationCategory(StrEnum):
    CITY = "city"
    BEACH = "beach"
    NATURE = "nature"
    CULTURAL = "cultural"
    OTHER = "other"


@dataclass
class Destination:
    trip_id: UUID
    name: str
    location: str
    category: DestinationCategory
    arrival_date: date
    departure_date: date
    position: int
    photo_url: str | None = None
    description: str = ""
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidDestinationError("Destination name must not be empty")
        if not self.location.strip():
            raise InvalidDestinationError("Destination location must not be empty")
        if self.departure_date < self.arrival_date:
            raise InvalidDestinationError("Destination departure must not be before its arrival")
        if self.position < FIRST_POSITION:
            raise InvalidDestinationError(f"Destination position must be at least {FIRST_POSITION}")
        if self.photo_url is not None and not self.photo_url.strip():
            raise InvalidDestinationError("Destination photo url must not be blank")

    @staticmethod
    def create(
        trip_id: UUID,
        name: str,
        location: str,
        category: DestinationCategory,
        arrival_date: date,
        departure_date: date,
        position: int,
        photo_url: str | None = None,
        description: str = "",
    ) -> "Destination":
        return Destination(
            trip_id=trip_id,
            name=name.strip(),
            location=location.strip(),
            category=category,
            arrival_date=arrival_date,
            departure_date=departure_date,
            position=position,
            photo_url=photo_url.strip() if photo_url is not None else None,
            description=description.strip(),
        )

    def update(
        self,
        name: str,
        location: str,
        category: DestinationCategory,
        arrival_date: date,
        departure_date: date,
        photo_url: str | None,
        description: str,
    ) -> None:
        updated = Destination.create(
            self.trip_id,
            name,
            location,
            category,
            arrival_date,
            departure_date,
            self.position,
            photo_url,
            description,
        )

        self.name = updated.name
        self.location = updated.location
        self.category = updated.category
        self.arrival_date = updated.arrival_date
        self.departure_date = updated.departure_date
        self.photo_url = updated.photo_url
        self.description = updated.description

    def move_to(self, position: int) -> None:
        if position < FIRST_POSITION:
            raise InvalidDestinationError(f"Destination position must be at least {FIRST_POSITION}")

        self.position = position


class ActivityCategory(StrEnum):
    TOUR = "tour"
    MEAL = "meal"
    LODGING = "lodging"
    TRANSPORT = "transport"
    OTHER = "other"


class ActivityStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"


@dataclass
class Activity:
    name: str
    category: ActivityCategory
    location: str
    description: str = ""
    photo_url: str | None = None
    average_rating: float = 0.0
    review_count: int = 0
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidActivityError("Activity name must not be empty")
        if not self.location.strip():
            raise InvalidActivityError("Activity location must not be empty")
        if self.photo_url is not None and not self.photo_url.strip():
            raise InvalidActivityError("Activity photo url must not be blank")
        if not 0 <= self.average_rating <= MAX_RATING:
            raise InvalidActivityError(
                f"Activity average rating must be between 0 and {MAX_RATING}"
            )
        if self.review_count < 0:
            raise InvalidActivityError("Activity review count must not be negative")

    @staticmethod
    def create(
        name: str,
        category: ActivityCategory,
        location: str,
        description: str = "",
        photo_url: str | None = None,
    ) -> "Activity":
        return Activity(
            name=name.strip(),
            category=category,
            location=location.strip(),
            description=description.strip(),
            photo_url=photo_url.strip() if photo_url is not None else None,
        )

    def recalculate_rating(self, ratings: list[int]) -> None:
        self.review_count = len(ratings)
        self.average_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0


@dataclass
class Review:
    activity_id: UUID
    user_id: UUID
    rating: int
    comment: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not MIN_RATING <= self.rating <= MAX_RATING:
            raise InvalidReviewError(f"Review rating must be between {MIN_RATING} and {MAX_RATING}")

    @staticmethod
    def create(
        activity_id: UUID, user_id: UUID, rating: int, comment: str | None = None
    ) -> "Review":
        return Review(
            activity_id=activity_id,
            user_id=user_id,
            rating=rating,
            comment=(comment.strip() or None) if comment is not None else None,
        )

    def update(self, rating: int, comment: str | None) -> None:
        updated = Review.create(self.activity_id, self.user_id, rating, comment)

        self.rating = updated.rating
        self.comment = updated.comment


@dataclass
class ScheduledActivity:
    destination_id: UUID
    activity_id: UUID
    starts_at: datetime | None = None
    duration_minutes: int | None = None
    planned_cost: float = 0.0
    status: ActivityStatus = ActivityStatus.PENDING
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if self.starts_at is not None and self.starts_at.tzinfo is not None:
            raise InvalidScheduledActivityError(
                "Activity start must be a local time without timezone"
            )
        if self.duration_minutes is not None and self.duration_minutes <= 0:
            raise InvalidScheduledActivityError("Activity duration must be positive")
        if self.planned_cost < 0:
            raise InvalidScheduledActivityError("Activity planned cost must not be negative")

    def update(
        self,
        starts_at: datetime | None,
        duration_minutes: int | None,
        planned_cost: float,
        status: ActivityStatus,
    ) -> None:
        updated = ScheduledActivity(
            self.destination_id, self.activity_id, starts_at, duration_minutes, planned_cost, status
        )

        self.starts_at = updated.starts_at
        self.duration_minutes = updated.duration_minutes
        self.planned_cost = updated.planned_cost
        self.status = updated.status


@dataclass(frozen=True)
class ReviewDetails:
    review: Review
    user: User


@dataclass(frozen=True)
class CollaboratorDetails:
    collaborator: Collaborator
    user: User


@dataclass(frozen=True)
class ScheduledActivityDetails:
    scheduled: ScheduledActivity
    activity: Activity
