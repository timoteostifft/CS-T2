from sqlalchemy import String, select
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

    def list_all(self) -> list[State]:
        with self._session_factory() as session:
            rows = session.scalars(select(StateModel).order_by(StateModel.name)).all()

            return [State(code=row.code, name=row.name) for row in rows]
