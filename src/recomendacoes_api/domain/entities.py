from dataclasses import dataclass, field
from uuid import UUID, uuid4

from recomendacoes_api.domain.exceptions import (
    InvalidCityError,
    InvalidPlaceError,
    InvalidStateError,
)

MAX_RATING = 5


@dataclass
class Place:
    name: str
    category: str
    city_id: int
    rating: float
    cost: float
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidPlaceError("Place name must not be empty")
        if not self.category.strip():
            raise InvalidPlaceError("Place category must not be empty")
        if self.city_id <= 0:
            raise InvalidPlaceError("Place city id must be positive")
        if not 0 <= self.rating <= MAX_RATING:
            raise InvalidPlaceError(f"Place rating must be between 0 and {MAX_RATING}")
        if self.cost < 0:
            raise InvalidPlaceError("Place cost must not be negative")

    @staticmethod
    def create(name: str, category: str, city_id: int, rating: float, cost: float) -> "Place":
        return Place(name=name, category=category, city_id=city_id, rating=rating, cost=cost)


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
