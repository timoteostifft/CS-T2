from datetime import UTC, datetime
from uuid import uuid4

from recomendacoes_api.domain.entities import Report


def test_create_report_hashes_ip_and_user_agent_into_device_hash():
    place_id = uuid4()

    report = Report.create(place_id=place_id, ip_address="10.0.0.1", user_agent="Firefox")

    assert report.place_id == place_id
    assert report.device_hash == Report.hash_device("10.0.0.1", "Firefox")
    assert "10.0.0.1" not in report.device_hash
    assert len(report.device_hash) == 64


def test_create_report_stamps_creation_time_in_utc():
    before = datetime.now(UTC)

    report = Report.create(place_id=uuid4(), ip_address="10.0.0.1", user_agent="Firefox")

    assert before <= report.created_at <= datetime.now(UTC)


def test_hash_device_is_deterministic():
    expected_hash = Report.hash_device("10.0.0.1", "Firefox")

    assert Report.hash_device("10.0.0.1", "Firefox") == expected_hash


def test_hash_device_differs_when_ip_or_user_agent_differs():
    base = Report.hash_device("10.0.0.1", "Firefox")

    assert Report.hash_device("10.0.0.2", "Firefox") != base
    assert Report.hash_device("10.0.0.1", "Chrome") != base
