from uuid import UUID

from recomendacoes_api.domain.entities import Destination


class MockDestinationRepository:
    def __init__(self, destinations: list[Destination] | None = None) -> None:
        self.destinations: list[Destination] = list(destinations or [])

    def list_by_trip(
        self, trip_id: UUID, limit: int | None = None, offset: int = 0
    ) -> list[Destination]:
        ordered = sorted(
            (item for item in self.destinations if item.trip_id == trip_id),
            key=lambda item: item.position,
        )
        end = None if limit is None else offset + limit

        return ordered[offset:end]

    def count_by_trip(self, trip_id: UUID) -> int:
        return len([item for item in self.destinations if item.trip_id == trip_id])

    def find_by_id(self, destination_id: UUID) -> Destination | None:
        return next((item for item in self.destinations if item.id == destination_id), None)

    def save(self, destination: Destination) -> None:
        self.destinations.append(destination)

    def update(self, destination: Destination) -> None:
        self.update_many([destination])

    def update_many(self, destinations: list[Destination]) -> None:
        changed = {item.id: item for item in destinations}
        self.destinations = [changed.get(item.id, item) for item in self.destinations]

    def delete(self, destination_id: UUID) -> None:
        self.destinations = [item for item in self.destinations if item.id != destination_id]
