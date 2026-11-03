from dataclasses import dataclass, field
from uuid import UUID, uuid4

from recomendacoes_api.domain.exceptions import (
    InvalidCityError,
    InvalidPlaceError,
    InvalidStateError,
)


@dataclass
class Place:
    name: str
    city: str
    category: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidPlaceError("Place name must not be empty")
        if not self.city.strip():
            raise InvalidPlaceError("Place city must not be empty")
        if not self.category.strip():
            raise InvalidPlaceError("Place category must not be empty")

    @staticmethod
    def create(name: str, city: str, category: str) -> "Place":
        return Place(name=name, city=city, category=category)


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
