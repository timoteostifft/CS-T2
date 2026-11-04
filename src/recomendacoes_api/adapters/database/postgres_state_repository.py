from sqlalchemy import String, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from recomendacoes_api.adapters.database.postgres_place_repository import Base
from recomendacoes_api.domain.entities import State


class StateModel(Base):
    __tablename__ = "states"

    code: Mapped[str] = mapped_column(String(2), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


class PostgresStateRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_all(self, limit: int | None = None, offset: int = 0) -> list[State]:
        query = select(StateModel).order_by(StateModel.name).offset(offset)

        if limit is not None:
            query = query.limit(limit)

        with self._session_factory() as session:
            rows = session.scalars(query).all()

            return [State(code=row.code, name=row.name) for row in rows]

    def count_all(self) -> int:
        with self._session_factory() as session:
            return session.scalar(select(func.count()).select_from(StateModel)) or 0
