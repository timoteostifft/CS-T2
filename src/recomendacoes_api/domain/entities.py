from dataclasses import dataclass, field
from uuid import UUID, uuid4

from recomendacoes_api.domain.exceptions import InvalidPlaceError


@dataclass
class Place:
    name: str
    category: str
    rating: float
    cost: float
    popularity: float
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvalidPlaceError("Place name must not be empty")
        if not self.category or not self.category.strip():
            raise InvalidPlaceError("Place category must not be empty")
        if self.rating < 0:
            raise InvalidPlaceError("Place rating must be greater than or equal to 0")
        if self.cost < 0:
            raise InvalidPlaceError("Place cost must be greater than or equal to 0")
        if self.popularity < 0:
            raise InvalidPlaceError("Place popularity must be greater than or equal to 0")

    @staticmethod
    def create(
        name: str,
        category: str,
        rating: float,
        cost: float,
        popularity: float,
    ) -> "Place":
        return Place(
            name=name,
            category=category,
            rating=float(rating),
            cost=float(cost),
            popularity=float(popularity),
        )
