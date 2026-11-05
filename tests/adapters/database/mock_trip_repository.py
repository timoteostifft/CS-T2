from uuid import UUID

from recomendacoes_api.domain.entities import Trip


class MockTripRepository:
    def __init__(self, trips: list[Trip] | None = None) -> None:
        self.trips: list[Trip] = list(trips or [])

    def list_by_user(self, user_id: UUID, limit: int | None = None, offset: int = 0) -> list[Trip]:
        owned = [trip for trip in self.trips if trip.can_view(user_id)]
        end = None if limit is None else offset + limit

        return owned[offset:end]

    def count_by_user(self, user_id: UUID) -> int:
        return len([trip for trip in self.trips if trip.can_view(user_id)])

    def find_by_id(self, trip_id: UUID) -> Trip | None:
        return next((trip for trip in self.trips if trip.id == trip_id), None)

    def find_by_invite_code(self, invite_code: str) -> Trip | None:
        return next((trip for trip in self.trips if trip.invite_code == invite_code), None)

    def save(self, trip: Trip) -> None:
        self.trips.append(trip)

    def update(self, trip: Trip) -> None:
        self.trips = [trip if item.id == trip.id else item for item in self.trips]

    def delete(self, trip_id: UUID) -> None:
        self.trips = [trip for trip in self.trips if trip.id != trip_id]
