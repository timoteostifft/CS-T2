from uuid import UUID

from recomendacoes_api.domain.entities import Review


class MockReviewRepository:
    def __init__(self, reviews: list[Review] | None = None) -> None:
        self._reviews = list(reviews or [])

    def find_by_place_and_device(self, place_id: UUID, device_id: str) -> Review | None:
        return next(
            (
                review
                for review in self._reviews
                if review.place_id == place_id and review.device_id == device_id
            ),
            None,
        )

    def list_by_place(self, place_id: UUID) -> list[Review]:
        return [review for review in self._reviews if review.place_id == place_id]

    def save(self, review: Review) -> None:
        self._reviews.append(review)

    def update(self, review: Review) -> None:
        self._reviews = [review if r.id == review.id else r for r in self._reviews]
