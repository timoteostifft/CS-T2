from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import Date, ForeignKey, String, delete, func, select
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from recomendacoes_api.adapters.database.postgres_user_repository import Base
from recomendacoes_api.domain.entities import Trip


class TripModel(Base):
    __tablename__ = "trips"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False, default="")
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)


def _to_entity(row: TripModel) -> Trip:
    return Trip(
        id=row.id,
        owner_id=row.owner_id,
        name=row.name,
        description=row.description,
        start_date=row.start_date,
        end_date=row.end_date,
    )


def _to_model(trip: Trip) -> TripModel:
    return TripModel(
        id=trip.id,
        owner_id=trip.owner_id,
        name=trip.name,
        description=trip.description,
        start_date=trip.start_date,
        end_date=trip.end_date,
    )


class PostgresTripRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_by_user(self, user_id: UUID, limit: int | None = None, offset: int = 0) -> list[Trip]:
        query = (
            select(TripModel)
            .where(TripModel.owner_id == user_id)
            .order_by(TripModel.start_date, TripModel.id)
            .offset(offset)
        )

        if limit is not None:
            query = query.limit(limit)

        with self._session_factory() as session:
            return [_to_entity(row) for row in session.scalars(query).all()]

    def count_by_user(self, user_id: UUID) -> int:
        query = select(func.count()).select_from(TripModel).where(TripModel.owner_id == user_id)

        with self._session_factory() as session:
            return session.scalar(query) or 0

    def find_by_id(self, trip_id: UUID) -> Trip | None:
        with self._session_factory() as session:
            row = session.get(TripModel, trip_id)

            return _to_entity(row) if row else None

    def save(self, trip: Trip) -> None:
        with self._session_factory() as session:
            session.add(_to_model(trip))
            session.commit()

    def update(self, trip: Trip) -> None:
        with self._session_factory() as session:
            session.merge(_to_model(trip))
            session.commit()

    def delete(self, trip_id: UUID) -> None:
        with self._session_factory() as session:
            session.execute(delete(TripModel).where(TripModel.id == trip_id))
            session.commit()
