from uuid import uuid4

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from recomendacoes_api.domain.entities import Place


class Base(DeclarativeBase):
    pass


class PlaceModel(Base):
    __tablename__ = "places"

    id: Mapped[str] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)


class PostgresPlaceRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_all(self) -> list[Place]:
        with self._session_factory() as session:
            rows = session.query(PlaceModel).all()
            return [
                Place(id=row.id, name=row.name, city=row.city, category=row.category)
                for row in rows
            ]
