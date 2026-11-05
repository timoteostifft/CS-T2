from uuid import UUID

from recomendacoes_api.domain.entities import Review


class MockReviewRepository:
    def __init__(self, reviews: list[Review] | None = None) -> None:
        self.reviews: list[Review] = list(reviews or [])

    def find_by_activity_and_user(self, activity_id: UUID, user_id: UUID) -> Review | None:
        return next(
            (
                item
                for item in self.reviews
                if item.activity_id == activity_id and item.user_id == user_id
            ),
            None,
        )

    def list_by_activity(
        self, activity_id: UUID, limit: int | None = None, offset: int = 0
    ) -> list[Review]:
        ordered = sorted(
            (item for item in self.reviews if item.activity_id == activity_id),
            key=lambda item: item.created_at,
            reverse=True,
        )
        end = None if limit is None else offset + limit

        return ordered[offset:end]

    def count_by_activity(self, activity_id: UUID) -> int:
        return len([item for item in self.reviews if item.activity_id == activity_id])

    def list_ratings_by_activity(self, activity_id: UUID) -> list[int]:
        return [item.rating for item in self.reviews if item.activity_id == activity_id]

    def save(self, review: Review) -> None:
        self.reviews.append(review)

    def update(self, review: Review) -> None:
        self.reviews = [review if item.id == review.id else item for item in self.reviews]
