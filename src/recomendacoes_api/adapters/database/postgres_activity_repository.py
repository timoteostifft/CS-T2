from uuid import UUID, uuid4

from sqlalchemy import String, func, select
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from recomendacoes_api.adapters.database.postgres_user_repository import Base
from recomendacoes_api.domain.entities import Activity, ActivityCategory


class ActivityModel(Base):
    __tablename__ = "activities"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    location: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False, default="")
    photo_url: Mapped[str | None] = mapped_column(String, nullable=True)


def _to_entity(row: ActivityModel) -> Activity:
    return Activity(
        id=row.id,
        name=row.name,
        category=ActivityCategory(row.category),
        location=row.location,
        description=row.description,
        photo_url=row.photo_url,
    )


class PostgresActivityRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_all(self, limit: int | None = None, offset: int = 0) -> list[Activity]:
        query = select(ActivityModel).order_by(ActivityModel.name, ActivityModel.id).offset(offset)

        if limit is not None:
            query = query.limit(limit)

        with self._session_factory() as session:
            return [_to_entity(row) for row in session.scalars(query).all()]

    def count_all(self) -> int:
        with self._session_factory() as session:
            return session.scalar(select(func.count()).select_from(ActivityModel)) or 0

    def list_by_ids(self, activity_ids: list[UUID]) -> list[Activity]:
        query = select(ActivityModel).where(ActivityModel.id.in_(activity_ids))

        with self._session_factory() as session:
            return [_to_entity(row) for row in session.scalars(query).all()]

    def find_by_id(self, activity_id: UUID) -> Activity | None:
        with self._session_factory() as session:
            row = session.get(ActivityModel, activity_id)

            return _to_entity(row) if row else None

    def save(self, activity: Activity) -> None:
        with self._session_factory() as session:
            session.add(
                ActivityModel(
                    id=activity.id,
                    name=activity.name,
                    category=activity.category.value,
                    location=activity.location,
                    description=activity.description,
                    photo_url=activity.photo_url,
                )
            )
            session.commit()
