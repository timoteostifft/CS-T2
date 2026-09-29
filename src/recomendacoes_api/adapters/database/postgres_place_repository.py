from uuid import UUID, uuid4

from sqlalchemy import Float, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from recomendacoes_api.domain.entities import Place


class Base(DeclarativeBase):
    pass


class PlaceModel(Base):
    __tablename__ = "places"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    cost: Mapped[float] = mapped_column(Float, nullable=False)
    popularity: Mapped[float] = mapped_column(Float, nullable=False)


class PostgresPlaceRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    @staticmethod
    def _to_entity(row: PlaceModel) -> Place:
        return Place(
            id=row.id,
            name=row.name,
            category=row.category,
            rating=row.rating,
            cost=row.cost,
            popularity=row.popularity,
        )

    def list_paginated(self, limit: int, offset: int) -> tuple[int, list[Place]]:
        with self._session_factory() as session:
            total = session.query(PlaceModel).count()
            rows = session.query(PlaceModel).offset(offset).limit(limit).all()
            return total, [self._to_entity(row) for row in rows]

    def list_all(self) -> list[Place]:
        with self._session_factory() as session:
            rows = session.query(PlaceModel).all()
            return [self._to_entity(row) for row in rows]

    def find_by_id(self, id: UUID) -> Place | None:
        with self._session_factory() as session:
            row = session.get(PlaceModel, id)
            return self._to_entity(row) if row else None

    def save(self, place: Place) -> Place:
        with self._session_factory() as session:
            model = PlaceModel(
                id=place.id,
                name=place.name,
                category=place.category,
                rating=place.rating,
                cost=place.cost,
                popularity=place.popularity,
            )
            session.add(model)
            session.commit()
            return place

    def update(self, place: Place) -> Place:
        with self._session_factory() as session:
            model = session.get(PlaceModel, place.id)
            if not model:
                return place
            model.name = place.name
            model.category = place.category
            model.rating = place.rating
            model.cost = place.cost
            model.popularity = place.popularity
            session.commit()
            return place

    def delete(self, id: UUID) -> bool:
        with self._session_factory() as session:
            model = session.get(PlaceModel, id)
            if not model:
                return False
            session.delete(model)
            session.commit()
            return True
