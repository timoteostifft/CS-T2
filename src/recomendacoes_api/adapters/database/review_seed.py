from hashlib import sha256
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy.orm import Session, sessionmaker

from recomendacoes_api.adapters.database.place_seed import load_places
from recomendacoes_api.adapters.database.postgres_place_repository import PostgresPlaceRepository
from recomendacoes_api.adapters.database.postgres_review_repository import PostgresReviewRepository
from recomendacoes_api.domain.entities import Place, Review

MIN_REVIEWS_PER_PLACE = 1
MAX_REVIEWS_PER_PLACE = 10
COMMENT_PERCENTAGE = 70

RATING_WEIGHTS = {1: 1, 2: 2, 3: 4, 4: 6, 5: 7}
WEIGHTED_RATINGS = [rating for rating, weight in RATING_WEIGHTS.items() for _ in range(weight)]

COMMENTS = {
    1: [
        "Decepcionante, não recomendo.",
        "Estava sujo e muito mal cuidado.",
        "Não vale a pena, perdi meu tempo.",
    ],
    2: [
        "Poderia ser bem melhor.",
        "Muito cheio e desorganizado.",
        "Esperava mais pelo que me falaram.",
    ],
    3: [
        "Razoável, nada de especial.",
        "Vale uma visita se estiver por perto.",
        "Bom, mas tem pontos a melhorar.",
    ],
    4: [
        "Muito bom, voltaria com certeza.",
        "Lugar bonito e bem cuidado.",
        "Ótimo passeio para fazer em família.",
    ],
    5: [
        "Simplesmente incrível, imperdível!",
        "Um dos melhores lugares que já visitei.",
        "Experiência perfeita, super recomendo.",
    ],
}


def _number(key: str) -> int:
    return int(sha256(key.encode()).hexdigest(), 16)


def _build_reviews(place: Place) -> list[Review]:
    base = f"recomendacoes-api/reviews/{place.id}"
    span = MAX_REVIEWS_PER_PLACE - MIN_REVIEWS_PER_PLACE + 1
    count = MIN_REVIEWS_PER_PLACE + _number(f"{base}/count") % span
    reviews: list[Review] = []

    for position in range(count):
        key = f"{base}/{position}"
        rating = WEIGHTED_RATINGS[_number(f"{key}/rating") % len(WEIGHTED_RATINGS)]
        options = COMMENTS[rating]
        has_comment = _number(f"{key}/has-comment") % 100 < COMMENT_PERCENTAGE
        comment = options[_number(f"{key}/comment") % len(options)] if has_comment else None

        reviews.append(
            Review(
                id=uuid5(NAMESPACE_URL, key),
                place_id=place.id,
                device_id=sha256(key.encode()).hexdigest(),
                rating=rating,
                comment=comment,
            )
        )

    return reviews


def seed_reviews(session_factory: sessionmaker[Session]) -> None:
    place_repository = PostgresPlaceRepository(session_factory)
    review_repository = PostgresReviewRepository(session_factory)

    for seed_place in load_places():
        place = place_repository.find_by_id(seed_place.id)

        if place is None or review_repository.list_by_place(place.id):
            continue

        reviews = _build_reviews(place)

        for review in reviews:
            review_repository.save(review)

        place.recalculate_rating([review.rating for review in reviews])

        place_repository.update(place)
