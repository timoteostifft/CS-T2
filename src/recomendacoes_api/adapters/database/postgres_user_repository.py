from uuid import UUID, uuid4

from sqlalchemy import String, select
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from recomendacoes_api.domain.entities import User


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)


def _to_entity(row: UserModel) -> User:
    return User(id=row.id, name=row.name, email=row.email, password_hash=row.password_hash)


class PostgresUserRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def find_by_id(self, user_id: UUID) -> User | None:
        with self._session_factory() as session:
            row = session.get(UserModel, user_id)

            return _to_entity(row) if row else None

    def find_by_email(self, email: str) -> User | None:
        with self._session_factory() as session:
            row = session.scalar(select(UserModel).where(UserModel.email == email))

            return _to_entity(row) if row else None

    def save(self, user: User) -> None:
        with self._session_factory() as session:
            session.add(
                UserModel(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    password_hash=user.password_hash,
                )
            )
            session.commit()
