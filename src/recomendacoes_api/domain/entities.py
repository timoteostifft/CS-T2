from dataclasses import dataclass, field
from uuid import UUID, uuid4

from recomendacoes_api.domain.exceptions import InvalidPlaceError


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
