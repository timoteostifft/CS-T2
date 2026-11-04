from uuid import UUID, uuid4

from sqlalchemy import Integer, String, select
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from recomendacoes_api.adapters.database.postgres_place_repository import Base
from recomendacoes_api.domain.entities import Review


class ReviewModel(Base):
    __tablename__ = "reviews"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    place_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    device_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(String, nullable=True)


def _to_entity(row: ReviewModel) -> Review:
    return Review(
        id=row.id,
        place_id=row.place_id,
        device_id=row.device_id,
        rating=row.rating,
        comment=row.comment,
    )


def _to_model(review: Review) -> ReviewModel:
    return ReviewModel(
        id=review.id,
        place_id=review.place_id,
        device_id=review.device_id,
        rating=review.rating,
        comment=review.comment,
    )


class PostgresReviewRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def find_by_place_and_device(self, place_id: UUID, device_id: str) -> Review | None:
        query = select(ReviewModel).where(
            ReviewModel.place_id == place_id,
            ReviewModel.device_id == device_id,
        )

        with self._session_factory() as session:
            row = session.scalar(query)

            return _to_entity(row) if row else None

    def list_by_place(self, place_id: UUID) -> list[Review]:
        query = select(ReviewModel).where(ReviewModel.place_id == place_id).order_by(ReviewModel.id)

        with self._session_factory() as session:
            return [_to_entity(row) for row in session.scalars(query).all()]

    def save(self, review: Review) -> None:
        with self._session_factory() as session:
            session.add(_to_model(review))

            session.commit()

    def update(self, review: Review) -> None:
        with self._session_factory() as session:
            session.merge(_to_model(review))

            session.commit()
