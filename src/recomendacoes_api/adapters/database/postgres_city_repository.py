from sqlalchemy import Integer, String, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from recomendacoes_api.adapters.database.postgres_place_repository import Base
from recomendacoes_api.domain.entities import City


class CityModel(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    state_code: Mapped[str] = mapped_column(String(2), nullable=False, index=True)


class PostgresCityRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_all(
        self, state_code: str | None = None, limit: int | None = None, offset: int = 0
    ) -> list[City]:
        query = select(CityModel).order_by(CityModel.name, CityModel.id).offset(offset)

        if state_code is not None:
            query = query.where(CityModel.state_code == state_code)

        if limit is not None:
            query = query.limit(limit)

        with self._session_factory() as session:
            rows = session.scalars(query).all()

            return [City(id=row.id, name=row.name, state_code=row.state_code) for row in rows]

    def count_all(self, state_code: str | None = None) -> int:
        query = select(func.count()).select_from(CityModel)

        if state_code is not None:
            query = query.where(CityModel.state_code == state_code)

        with self._session_factory() as session:
            return session.scalar(query) or 0

    def exists_by_id(self, city_id: int) -> bool:
        with self._session_factory() as session:
            return session.get(CityModel, city_id) is not None
