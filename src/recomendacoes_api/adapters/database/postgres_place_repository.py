from uuid import UUID, uuid4

from sqlalchemy import Boolean, Float, Integer, Select, String, func, select
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from recomendacoes_api.domain.entities import Place


class Base(DeclarativeBase):
    pass


class PlaceModel(Base):
    __tablename__ = "places"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    city_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    cost: Mapped[float] = mapped_column(Float, nullable=False)
    average_rating: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


SORT_CLAUSES = {
    "name": (PlaceModel.name.asc(), PlaceModel.id.asc()),
    "cost": (PlaceModel.cost.asc(), PlaceModel.name.asc(), PlaceModel.id.asc()),
    "rating": (PlaceModel.average_rating.desc(), PlaceModel.name.asc(), PlaceModel.id.asc()),
}


def _to_entity(row: PlaceModel) -> Place:
    return Place(
        id=row.id,
        name=row.name,
        category=row.category,
        city_id=row.city_id,
        cost=row.cost,
        average_rating=row.average_rating,
        review_count=row.review_count,
        archived=row.archived,
    )


def _to_model(place: Place) -> PlaceModel:
    return PlaceModel(
        id=place.id,
        name=place.name,
        category=place.category,
        city_id=place.city_id,
        cost=place.cost,
        average_rating=place.average_rating,
        review_count=place.review_count,
        archived=place.archived,
    )


def _apply_filters(
    query: Select,
    category: str | None,
    city_id: int | None,
    min_rating: float | None,
    max_cost: float | None,
) -> Select:
    query = query.where(PlaceModel.archived.is_(False))

    if category is not None:
        query = query.where(PlaceModel.category == category)
    if city_id is not None:
        query = query.where(PlaceModel.city_id == city_id)
    if min_rating is not None:
        query = query.where(PlaceModel.average_rating >= min_rating)
    if max_cost is not None:
        query = query.where(PlaceModel.cost <= max_cost)

    return query


class PostgresPlaceRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_all(
        self,
        category: str | None = None,
        city_id: int | None = None,
        min_rating: float | None = None,
        max_cost: float | None = None,
        sort: str = "name",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Place]:
        query = _apply_filters(select(PlaceModel), category, city_id, min_rating, max_cost)
        query = query.order_by(*SORT_CLAUSES[sort]).offset(offset)

        if limit is not None:
            query = query.limit(limit)

        with self._session_factory() as session:
            return [_to_entity(row) for row in session.scalars(query).all()]

    def count_all(
        self,
        category: str | None = None,
        city_id: int | None = None,
        min_rating: float | None = None,
        max_cost: float | None = None,
    ) -> int:
        query = select(func.count()).select_from(PlaceModel)
        query = _apply_filters(query, category, city_id, min_rating, max_cost)

        with self._session_factory() as session:
            return session.scalar(query) or 0

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
