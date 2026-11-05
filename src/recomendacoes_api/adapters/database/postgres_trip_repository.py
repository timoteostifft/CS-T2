from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import (
    Date,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
    delete,
    func,
    or_,
    select,
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship, sessionmaker

from recomendacoes_api.adapters.database.postgres_user_repository import Base
from recomendacoes_api.domain.entities import Collaborator, CollaboratorRole, Trip


class CollaboratorModel(Base):
    __tablename__ = "trip_collaborators"
    __table_args__ = (UniqueConstraint("trip_id", "user_id"),)

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    trip_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String, nullable=False)


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
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    invite_code: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    collaborators: Mapped[list[CollaboratorModel]] = relationship(
        lazy="selectin", cascade="all, delete-orphan"
    )


def _to_entity(row: TripModel) -> Trip:
    return Trip(
        id=row.id,
        owner_id=row.owner_id,
        name=row.name,
        description=row.description,
        start_date=row.start_date,
        end_date=row.end_date,
        budget=row.budget,
        invite_code=row.invite_code,
        collaborators=[
            Collaborator(id=item.id, user_id=item.user_id, role=CollaboratorRole(item.role))
            for item in row.collaborators
        ],
    )


def _to_model(trip: Trip) -> TripModel:
    return TripModel(
        id=trip.id,
        owner_id=trip.owner_id,
        name=trip.name,
        description=trip.description,
        start_date=trip.start_date,
        end_date=trip.end_date,
        budget=trip.budget,
        invite_code=trip.invite_code,
        collaborators=[
            CollaboratorModel(
                id=item.id, trip_id=trip.id, user_id=item.user_id, role=item.role.value
            )
            for item in trip.collaborators
        ],
    )


def _participates(user_id: UUID):
    shared_trip_ids = select(CollaboratorModel.trip_id).where(CollaboratorModel.user_id == user_id)

    return or_(TripModel.owner_id == user_id, TripModel.id.in_(shared_trip_ids))


class PostgresTripRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_by_user(self, user_id: UUID, limit: int | None = None, offset: int = 0) -> list[Trip]:
        query = (
            select(TripModel)
            .where(_participates(user_id))
            .order_by(TripModel.start_date, TripModel.id)
            .offset(offset)
        )

        if limit is not None:
            query = query.limit(limit)

        with self._session_factory() as session:
            return [_to_entity(row) for row in session.scalars(query).all()]

    def count_by_user(self, user_id: UUID) -> int:
        query = select(func.count()).select_from(TripModel).where(_participates(user_id))

        with self._session_factory() as session:
            return session.scalar(query) or 0

    def find_by_id(self, trip_id: UUID) -> Trip | None:
        with self._session_factory() as session:
            row = session.get(TripModel, trip_id)

            return _to_entity(row) if row else None

    def find_by_invite_code(self, invite_code: str) -> Trip | None:
        with self._session_factory() as session:
            row = session.scalar(select(TripModel).where(TripModel.invite_code == invite_code))

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
            session.execute(delete(CollaboratorModel).where(CollaboratorModel.trip_id == trip_id))
            session.execute(delete(TripModel).where(TripModel.id == trip_id))
            session.commit()
