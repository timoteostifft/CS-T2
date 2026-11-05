from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from recomendacoes_api.application.use_cases import ReportPlaceUseCase
from recomendacoes_api.domain.entities import Place, Report
from recomendacoes_api.domain.exceptions import DuplicateReportError, PlaceNotFoundError
from tests.adapters.database.mock_place_repository import MockPlaceRepository
from tests.adapters.database.mock_report_repository import MockReportRepository

EVER = datetime.min.replace(tzinfo=UTC)


def build_place(archived: bool = False) -> Place:
    return Place(
        name="Praia do Rosa",
        category="beach",
        city_id=4207304,
        cost=30.0,
        archived=archived,
    )


def past_report(place: Place, ip_address: str, hours_ago: int) -> Report:
    return Report(
        place_id=place.id,
        device_hash=Report.hash_device(ip_address, "Firefox"),
        created_at=datetime.now(UTC) - timedelta(hours=hours_ago),
    )


def test_report_place_saves_report_without_archiving_below_threshold():
    place = build_place()
    places = MockPlaceRepository([place])
    reports = MockReportRepository()
    use_case = ReportPlaceUseCase(places, reports)

    report = use_case.execute(place_id=place.id, ip_address="10.0.0.1", user_agent="Firefox")
    use_case.execute(place_id=place.id, ip_address="10.0.0.2", user_agent="Firefox")

    assert report.place_id == place.id
    assert report.device_hash == Report.hash_device("10.0.0.1", "Firefox")
    assert reports.count_devices_by_place_since(place.id, EVER) == 2
    assert places.find_by_id(place.id).archived is False


def test_report_place_archives_place_on_third_distinct_device():
    place = build_place()
    places = MockPlaceRepository([place])
    use_case = ReportPlaceUseCase(places, MockReportRepository())

    for ip_address in ["10.0.0.1", "10.0.0.2", "10.0.0.3"]:
        use_case.execute(place_id=place.id, ip_address=ip_address, user_agent="Firefox")

    assert places.find_by_id(place.id).archived is True


def test_report_place_treats_same_ip_with_other_user_agent_as_another_device():
    place = build_place()
    places = MockPlaceRepository([place])
    use_case = ReportPlaceUseCase(places, MockReportRepository())

    for user_agent in ["Firefox", "Chrome", "Safari"]:
        use_case.execute(place_id=place.id, ip_address="10.0.0.1", user_agent=user_agent)

    assert places.find_by_id(place.id).archived is True


def test_report_place_ignores_reports_older_than_the_window():
    place = build_place()
    places = MockPlaceRepository([place])
    reports = MockReportRepository(
        [past_report(place, "10.0.0.1", hours_ago=25), past_report(place, "10.0.0.2", hours_ago=30)]
    )
    use_case = ReportPlaceUseCase(places, reports)

    use_case.execute(place_id=place.id, ip_address="10.0.0.3", user_agent="Firefox")

    assert places.find_by_id(place.id).archived is False


def test_report_place_counts_reports_inside_the_window():
    place = build_place()
    places = MockPlaceRepository([place])
    reports = MockReportRepository(
        [past_report(place, "10.0.0.1", hours_ago=23), past_report(place, "10.0.0.2", hours_ago=1)]
    )
    use_case = ReportPlaceUseCase(places, reports)

    use_case.execute(place_id=place.id, ip_address="10.0.0.3", user_agent="Firefox")

    assert places.find_by_id(place.id).archived is True


def test_report_place_from_same_device_inside_window_raises_duplicate():
    place = build_place()
    reports = MockReportRepository([past_report(place, "10.0.0.1", hours_ago=2)])
    use_case = ReportPlaceUseCase(MockPlaceRepository([place]), reports)

    with pytest.raises(DuplicateReportError):
        use_case.execute(place_id=place.id, ip_address="10.0.0.1", user_agent="Firefox")

    assert reports.count_devices_by_place_since(place.id, EVER) == 1


def test_report_place_from_same_device_after_window_is_accepted():
    place = build_place()
    reports = MockReportRepository([past_report(place, "10.0.0.1", hours_ago=25)])
    use_case = ReportPlaceUseCase(MockPlaceRepository([place]), reports)

    report = use_case.execute(place_id=place.id, ip_address="10.0.0.1", user_agent="Firefox")

    assert report.place_id == place.id


def test_report_missing_place_raises_not_found():
    reports = MockReportRepository()
    use_case = ReportPlaceUseCase(MockPlaceRepository(), reports)
    missing_id = uuid4()

    with pytest.raises(PlaceNotFoundError):
        use_case.execute(place_id=missing_id, ip_address="10.0.0.1", user_agent="Firefox")

    assert reports.count_devices_by_place_since(missing_id, EVER) == 0


def test_report_archived_place_raises_not_found():
    place = build_place(archived=True)
    use_case = ReportPlaceUseCase(MockPlaceRepository([place]), MockReportRepository())

    with pytest.raises(PlaceNotFoundError):
        use_case.execute(place_id=place.id, ip_address="10.0.0.1", user_agent="Firefox")
