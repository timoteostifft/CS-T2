from datetime import datetime
from uuid import UUID

from recomendacoes_api.domain.entities import Report


class MockReportRepository:
    def __init__(self, reports: list[Report] | None = None) -> None:
        self._reports = list(reports or [])

    def exists_by_place_and_device_since(
        self, place_id: UUID, device_hash: str, since: datetime
    ) -> bool:
        return any(report.device_hash == device_hash for report in self._filter(place_id, since))

    def count_devices_by_place_since(self, place_id: UUID, since: datetime) -> int:
        return len({report.device_hash for report in self._filter(place_id, since)})

    def save(self, report: Report) -> None:
        self._reports.append(report)

    def _filter(self, place_id: UUID, since: datetime) -> list[Report]:
        return [
            report
            for report in self._reports
            if report.place_id == place_id and report.created_at >= since
        ]
