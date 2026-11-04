from uuid import UUID, uuid4

from sqlalchemy import Float, Integer, String, func, select
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
    city_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    cost: Mapped[float] = mapped_column(Float, nullable=False)


def _to_entity(row: PlaceModel) -> Place:
    return Place(
        id=row.id,
        name=row.name,
        category=row.category,
        city_id=row.city_id,
        rating=row.rating,
        cost=row.cost,
    )


def _to_model(place: Place) -> PlaceModel:
    return PlaceModel(
        id=place.id,
        name=place.name,
        category=place.category,
        city_id=place.city_id,
        rating=place.rating,
        cost=place.cost,
    )


class PostgresPlaceRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_all(self, limit: int | None = None, offset: int = 0) -> list[Place]:
        query = select(PlaceModel).order_by(PlaceModel.name, PlaceModel.id).offset(offset)

        if limit is not None:
            query = query.limit(limit)

        with self._session_factory() as session:
            return [_to_entity(row) for row in session.scalars(query).all()]

    def count_all(self) -> int:
        with self._session_factory() as session:
            return session.scalar(select(func.count()).select_from(PlaceModel)) or 0

    def find_by_id(self, place_id: UUID) -> Place | None:
        with self._session_factory() as session:
            row = session.get(PlaceModel, place_id)

            return _to_entity(row) if row else None

    def save(self, place: Place) -> None:
        with self._session_factory() as session:
            session.add(_to_model(place))

            session.commit()

    def update(self, place: Place) -> None:
        with self._session_factory() as session:
            session.merge(_to_model(place))

            session.commit()

    def delete(self, place_id: UUID) -> None:
        with self._session_factory() as session:
            row = session.get(PlaceModel, place_id)

            if row is not None:
                session.delete(row)

                session.commit()
