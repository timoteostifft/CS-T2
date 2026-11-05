from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import UUID, uuid4

from recomendacoes_api.domain.exceptions import (
    InvalidCityError,
    InvalidPlaceError,
    InvalidReviewError,
    InvalidStateError,
)

MIN_RATING = 1
MAX_RATING = 5
PLACE_SORT_FIELDS = ("name", "rating", "cost")
REPORT_WINDOW = timedelta(hours=24)
REPORTS_TO_ARCHIVE = 3


@dataclass
class Place:
    name: str
    category: str
    city_id: int
    cost: float
    average_rating: float = 0.0
    review_count: int = 0
    archived: bool = False
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidPlaceError("Place name must not be empty")
        if not self.category.strip():
            raise InvalidPlaceError("Place category must not be empty")
        if self.city_id <= 0:
            raise InvalidPlaceError("Place city id must be positive")
        if self.cost < 0:
            raise InvalidPlaceError("Place cost must not be negative")
        if not 0 <= self.average_rating <= MAX_RATING:
            raise InvalidPlaceError(f"Place average rating must be between 0 and {MAX_RATING}")
        if self.review_count < 0:
            raise InvalidPlaceError("Place review count must not be negative")

    @staticmethod
    def create(name: str, category: str, city_id: int, cost: float) -> "Place":
        return Place(name=name, category=category, city_id=city_id, cost=cost)

    def recalculate_rating(self, ratings: list[int]) -> None:
        self.review_count = len(ratings)
        self.average_rating = sum(ratings) / len(ratings) if ratings else 0.0

    def archive(self) -> None:
        self.archived = True


@dataclass
class Review:
    place_id: UUID
    device_id: str
    rating: int
    comment: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.device_id.strip():
            raise InvalidReviewError("Review device id must not be empty")
        if not MIN_RATING <= self.rating <= MAX_RATING:
            raise InvalidReviewError(f"Review rating must be between {MIN_RATING} and {MAX_RATING}")

    @staticmethod
    def create(
        place_id: UUID,
        device_id: str,
        rating: int,
        comment: str | None = None,
    ) -> "Review":
        return Review(place_id=place_id, device_id=device_id, rating=rating, comment=comment)


@dataclass
class Report:
    place_id: UUID
    device_hash: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    id: UUID = field(default_factory=uuid4)

    @staticmethod
    def create(place_id: UUID, ip_address: str, user_agent: str) -> "Report":
        return Report(place_id=place_id, device_hash=Report.hash_device(ip_address, user_agent))

    @staticmethod
    def hash_device(ip_address: str, user_agent: str) -> str:
        return sha256(f"{ip_address}|{user_agent}".encode()).hexdigest()


@dataclass(frozen=True)
class State:
    code: str
    name: str

    def __post_init__(self) -> None:
        if len(self.code) != 2 or not self.code.isalpha() or not self.code.isupper():
            raise InvalidStateError("State code must be two uppercase letters")
        if not self.name.strip():
            raise InvalidStateError("State name must not be empty")


@dataclass(frozen=True)
class City:
    id: int
    name: str
    state_code: str

    def __post_init__(self) -> None:
        if self.id <= 0:
            raise InvalidCityError("City id must be positive")
        if not self.name.strip():
            raise InvalidCityError("City name must not be empty")
        if not self.state_code.strip():
            raise InvalidCityError("City state code must not be empty")
