from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, delete, func, select
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from recomendacoes_api.adapters.database.postgres_user_repository import Base
from recomendacoes_api.domain.entities import ActivityStatus, ScheduledActivity


class ScheduledActivityModel(Base):
    __tablename__ = "scheduled_activities"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    destination_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), index=True
    )
    activity_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("activities.id"), index=True
    )
    starts_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    planned_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String, nullable=False)


def _to_entity(row: ScheduledActivityModel) -> ScheduledActivity:
    return ScheduledActivity(
        id=row.id,
        destination_id=row.destination_id,
        activity_id=row.activity_id,
        starts_at=row.starts_at,
        duration_minutes=row.duration_minutes,
        planned_cost=row.planned_cost,
        status=ActivityStatus(row.status),
    )


def _to_model(scheduled: ScheduledActivity) -> ScheduledActivityModel:
    return ScheduledActivityModel(
        id=scheduled.id,
        destination_id=scheduled.destination_id,
        activity_id=scheduled.activity_id,
        starts_at=scheduled.starts_at,
        duration_minutes=scheduled.duration_minutes,
        planned_cost=scheduled.planned_cost,
        status=scheduled.status.value,
    )


class PostgresScheduledActivityRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_by_destination(
        self, destination_id: UUID, limit: int | None = None, offset: int = 0
    ) -> list[ScheduledActivity]:
        query = (
            select(ScheduledActivityModel)
            .where(ScheduledActivityModel.destination_id == destination_id)
            .order_by(
                ScheduledActivityModel.starts_at.asc().nulls_last(), ScheduledActivityModel.id
            )
            .offset(offset)
        )

        if limit is not None:
            query = query.limit(limit)

        with self._session_factory() as session:
            return [_to_entity(row) for row in session.scalars(query).all()]

    def count_by_destination(self, destination_id: UUID) -> int:
        query = (
            select(func.count())
            .select_from(ScheduledActivityModel)
            .where(ScheduledActivityModel.destination_id == destination_id)
        )

        with self._session_factory() as session:
            return session.scalar(query) or 0

    def find_by_id(self, scheduled_id: UUID) -> ScheduledActivity | None:
        with self._session_factory() as session:
            row = session.get(ScheduledActivityModel, scheduled_id)

            return _to_entity(row) if row else None

    def save(self, scheduled: ScheduledActivity) -> None:
        with self._session_factory() as session:
            session.add(_to_model(scheduled))
            session.commit()

    def update(self, scheduled: ScheduledActivity) -> None:
        with self._session_factory() as session:
            session.merge(_to_model(scheduled))
            session.commit()

    def delete(self, scheduled_id: UUID) -> None:
        with self._session_factory() as session:
            session.execute(
                delete(ScheduledActivityModel).where(ScheduledActivityModel.id == scheduled_id)
            )
            session.commit()
