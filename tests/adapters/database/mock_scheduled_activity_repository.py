from datetime import datetime
from uuid import UUID

from recomendacoes_api.domain.entities import ScheduledActivity


class MockScheduledActivityRepository:
    def __init__(self, scheduled_items: list[ScheduledActivity] | None = None) -> None:
        self.scheduled_items: list[ScheduledActivity] = list(scheduled_items or [])

    def list_by_destination(
        self, destination_id: UUID, limit: int | None = None, offset: int = 0
    ) -> list[ScheduledActivity]:
        ordered = sorted(
            (item for item in self.scheduled_items if item.destination_id == destination_id),
            key=lambda item: (item.starts_at is None, item.starts_at or datetime.min),
        )
        end = None if limit is None else offset + limit

        return ordered[offset:end]

    def count_by_destination(self, destination_id: UUID) -> int:
        return len([item for item in self.scheduled_items if item.destination_id == destination_id])

    def find_by_id(self, scheduled_id: UUID) -> ScheduledActivity | None:
        return next((item for item in self.scheduled_items if item.id == scheduled_id), None)

    def save(self, scheduled: ScheduledActivity) -> None:
        self.scheduled_items.append(scheduled)

    def update(self, scheduled: ScheduledActivity) -> None:
        self.scheduled_items = [
            scheduled if item.id == scheduled.id else item for item in self.scheduled_items
        ]

    def delete(self, scheduled_id: UUID) -> None:
        self.scheduled_items = [item for item in self.scheduled_items if item.id != scheduled_id]
