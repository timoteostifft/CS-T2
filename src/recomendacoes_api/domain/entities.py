from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from uuid import UUID, uuid4

from recomendacoes_api.domain.exceptions import (
    InvalidDestinationError,
    InvalidTripError,
    InvalidUserError,
)

MIN_PASSWORD_LENGTH = 8
FIRST_POSITION = 1


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
class Trip:
    name: str
    start_date: date
    end_date: date
    owner_id: UUID
    description: str = ""
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidTripError("Trip name must not be empty")
        if self.end_date < self.start_date:
            raise InvalidTripError("Trip end date must not be before its start date")

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
