from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import Date, ForeignKey, Integer, String, delete, func, select
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from recomendacoes_api.adapters.database.postgres_user_repository import Base
from recomendacoes_api.domain.entities import Destination, DestinationCategory


class DestinationModel(Base):
    __tablename__ = "destinations"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    trip_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    arrival_date: Mapped[date] = mapped_column(Date, nullable=False)
    departure_date: Mapped[date] = mapped_column(Date, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=False, default="")


def _to_entity(row: DestinationModel) -> Destination:
    return Destination(
        id=row.id,
        trip_id=row.trip_id,
        position=row.position,
        name=row.name,
        location=row.location,
        category=DestinationCategory(row.category),
        arrival_date=row.arrival_date,
        departure_date=row.departure_date,
        photo_url=row.photo_url,
        description=row.description,
    )


def _to_model(destination: Destination) -> DestinationModel:
    return DestinationModel(
        id=destination.id,
        trip_id=destination.trip_id,
        position=destination.position,
        name=destination.name,
        location=destination.location,
        category=destination.category.value,
        arrival_date=destination.arrival_date,
        departure_date=destination.departure_date,
        photo_url=destination.photo_url,
        description=destination.description,
    )


class PostgresDestinationRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_by_trip(
        self, trip_id: UUID, limit: int | None = None, offset: int = 0
    ) -> list[Destination]:
        query = (
            select(DestinationModel)
            .where(DestinationModel.trip_id == trip_id)
            .order_by(DestinationModel.position)
            .offset(offset)
        )

        if limit is not None:
            query = query.limit(limit)

        with self._session_factory() as session:
            return [_to_entity(row) for row in session.scalars(query).all()]

    def count_by_trip(self, trip_id: UUID) -> int:
        query = (
            select(func.count())
            .select_from(DestinationModel)
            .where(DestinationModel.trip_id == trip_id)
        )

        with self._session_factory() as session:
            return session.scalar(query) or 0

    def find_by_id(self, destination_id: UUID) -> Destination | None:
        with self._session_factory() as session:
            row = session.get(DestinationModel, destination_id)

            return _to_entity(row) if row else None

    def save(self, destination: Destination) -> None:
        with self._session_factory() as session:
            session.add(_to_model(destination))
            session.commit()

    def update(self, destination: Destination) -> None:
        self.update_many([destination])

    def update_many(self, destinations: list[Destination]) -> None:
        with self._session_factory() as session:
            for destination in destinations:
                session.merge(_to_model(destination))

            session.commit()

    def delete(self, destination_id: UUID) -> None:
        with self._session_factory() as session:
            session.execute(delete(DestinationModel).where(DestinationModel.id == destination_id))
            session.commit()
