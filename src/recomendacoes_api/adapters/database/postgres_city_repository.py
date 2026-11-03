from sqlalchemy import Integer, String, select
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

    def list_all(self, state_code: str | None = None) -> list[City]:
        query = select(CityModel).order_by(CityModel.name)

        if state_code is not None:
            query = query.where(CityModel.state_code == state_code)

        with self._session_factory() as session:
            rows = session.scalars(query).all()

            return [City(id=row.id, name=row.name, state_code=row.state_code) for row in rows]
