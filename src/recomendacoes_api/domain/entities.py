from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Place:
    name: str
    city: str
    category: str
    id: UUID = field(default_factory=uuid4)

    @staticmethod
    def create(name: str, city: str, category: str) -> "Place":
        return Place(name=name, city=city, category=category)
