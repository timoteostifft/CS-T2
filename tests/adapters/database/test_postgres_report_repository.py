from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from recomendacoes_api.adapters.database.postgres_report_repository import PostgresReportRepository
from recomendacoes_api.domain.entities import Report

NOW = datetime.now(UTC)
WINDOW_START = NOW - timedelta(hours=24)


def build_report(
    place_id: UUID | None = None, device_hash: str = "device-a", hours_ago: int = 0
) -> Report:
    return Report(
        place_id=place_id or uuid4(),
        device_hash=device_hash,
        created_at=NOW - timedelta(hours=hours_ago),
    )


def test_exists_by_place_and_device_since_finds_a_recent_report(session_factory):
    repository = PostgresReportRepository(session_factory)
    report = build_report(hours_ago=1)

    repository.save(report)

    assert repository.exists_by_place_and_device_since(
        report.place_id, report.device_hash, WINDOW_START
    )


def test_exists_by_place_and_device_since_ignores_reports_before_since(session_factory):
    repository = PostgresReportRepository(session_factory)
    report = build_report(hours_ago=25)

    repository.save(report)

    assert not repository.exists_by_place_and_device_since(
        report.place_id, report.device_hash, WINDOW_START
    )


def test_exists_by_place_and_device_since_ignores_other_places_and_devices(session_factory):
    repository = PostgresReportRepository(session_factory)
    report = build_report()

    repository.save(report)

    assert not repository.exists_by_place_and_device_since(uuid4(), "device-a", WINDOW_START)
    assert not repository.exists_by_place_and_device_since(
        report.place_id, "device-b", WINDOW_START
    )


def test_count_devices_by_place_since_counts_distinct_recent_devices(session_factory):
    repository = PostgresReportRepository(session_factory)
    place_id = uuid4()

    repository.save(build_report(place_id, "device-a", hours_ago=1))
    repository.save(build_report(place_id, "device-a", hours_ago=2))
    repository.save(build_report(place_id, "device-b", hours_ago=3))
    repository.save(build_report(place_id, "device-c", hours_ago=30))
    repository.save(build_report(uuid4(), "device-d", hours_ago=1))

    assert repository.count_devices_by_place_since(place_id, WINDOW_START) == 2


def test_count_devices_by_place_since_returns_zero_without_reports(session_factory):
    repository = PostgresReportRepository(session_factory)

    assert repository.count_devices_by_place_since(uuid4(), WINDOW_START) == 0
