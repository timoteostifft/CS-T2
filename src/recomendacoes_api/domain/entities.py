from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

from recomendacoes_api.domain.exceptions import InvalidTripError, InvalidUserError

MIN_PASSWORD_LENGTH = 8


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
