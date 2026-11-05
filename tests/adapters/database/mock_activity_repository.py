from uuid import UUID

from recomendacoes_api.domain.entities import Activity


class MockActivityRepository:
    def __init__(self, activities: list[Activity] | None = None) -> None:
        self.activities: list[Activity] = list(activities or [])

    def list_all(self, limit: int | None = None, offset: int = 0) -> list[Activity]:
        ordered = sorted(self.activities, key=lambda item: item.name)
        end = None if limit is None else offset + limit

        return ordered[offset:end]

    def count_all(self) -> int:
        return len(self.activities)

    def list_by_ids(self, activity_ids: list[UUID]) -> list[Activity]:
        return [item for item in self.activities if item.id in activity_ids]

    def find_by_id(self, activity_id: UUID) -> Activity | None:
        return next((item for item in self.activities if item.id == activity_id), None)

    def save(self, activity: Activity) -> None:
        self.activities.append(activity)
