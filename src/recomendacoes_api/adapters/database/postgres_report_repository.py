from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func, select
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from recomendacoes_api.adapters.database.postgres_place_repository import Base
from recomendacoes_api.domain.entities import Report


class ReportModel(Base):
    __tablename__ = "reports"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    place_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    device_hash: Mapped[str] = mapped_column(String, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def _to_model(report: Report) -> ReportModel:
    return ReportModel(
        id=report.id,
        place_id=report.place_id,
        device_hash=report.device_hash,
        created_at=report.created_at,
    )


class PostgresReportRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def exists_by_place_and_device_since(
        self, place_id: UUID, device_hash: str, since: datetime
    ) -> bool:
        query = select(ReportModel.id).where(
            ReportModel.place_id == place_id,
            ReportModel.device_hash == device_hash,
            ReportModel.created_at >= since,
        )

        with self._session_factory() as session:
            return session.scalar(query.limit(1)) is not None

    def count_devices_by_place_since(self, place_id: UUID, since: datetime) -> int:
        query = select(func.count(func.distinct(ReportModel.device_hash))).where(
            ReportModel.place_id == place_id,
            ReportModel.created_at >= since,
        )

        with self._session_factory() as session:
            return session.scalar(query) or 0

    def save(self, report: Report) -> None:
        with self._session_factory() as session:
            session.add(_to_model(report))

            session.commit()
