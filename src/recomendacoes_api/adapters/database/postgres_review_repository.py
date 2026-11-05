from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func, select
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from recomendacoes_api.adapters.database.postgres_user_repository import Base
from recomendacoes_api.domain.entities import Review


class ReviewModel(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("activity_id", "user_id"),)

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    activity_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("activities.id"), index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def _to_entity(row: ReviewModel) -> Review:
    created_at = row.created_at if row.created_at.tzinfo else row.created_at.replace(tzinfo=UTC)

    return Review(
        id=row.id,
        activity_id=row.activity_id,
        user_id=row.user_id,
        rating=row.rating,
        comment=row.comment,
        created_at=created_at,
    )


def _to_model(review: Review) -> ReviewModel:
    return ReviewModel(
        id=review.id,
        activity_id=review.activity_id,
        user_id=review.user_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
    )


class PostgresReviewRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def find_by_activity_and_user(self, activity_id: UUID, user_id: UUID) -> Review | None:
        query = select(ReviewModel).where(
            ReviewModel.activity_id == activity_id, ReviewModel.user_id == user_id
        )

        with self._session_factory() as session:
            row = session.scalar(query)

            return _to_entity(row) if row else None

    def list_by_activity(
        self, activity_id: UUID, limit: int | None = None, offset: int = 0
    ) -> list[Review]:
        query = (
            select(ReviewModel)
            .where(ReviewModel.activity_id == activity_id)
            .order_by(ReviewModel.created_at.desc(), ReviewModel.id)
            .offset(offset)
        )

        if limit is not None:
            query = query.limit(limit)

        with self._session_factory() as session:
            return [_to_entity(row) for row in session.scalars(query).all()]

    def count_by_activity(self, activity_id: UUID) -> int:
        query = (
            select(func.count())
            .select_from(ReviewModel)
            .where(ReviewModel.activity_id == activity_id)
        )

        with self._session_factory() as session:
            return session.scalar(query) or 0

    def list_ratings_by_activity(self, activity_id: UUID) -> list[int]:
        query = select(ReviewModel.rating).where(ReviewModel.activity_id == activity_id)

        with self._session_factory() as session:
            return list(session.scalars(query).all())

    def save(self, review: Review) -> None:
        with self._session_factory() as session:
            session.add(_to_model(review))
            session.commit()

    def update(self, review: Review) -> None:
        with self._session_factory() as session:
            session.merge(_to_model(review))
            session.commit()
