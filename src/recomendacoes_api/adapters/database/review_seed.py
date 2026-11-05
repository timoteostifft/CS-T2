from hashlib import sha256
from random import Random
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy.orm import Session, sessionmaker

from recomendacoes_api.adapters.database.place_seed import load_places
from recomendacoes_api.adapters.database.postgres_place_repository import PostgresPlaceRepository
from recomendacoes_api.adapters.database.postgres_review_repository import PostgresReviewRepository
from recomendacoes_api.domain.entities import Place, Review

MIN_REVIEWS_PER_PLACE = 1
MAX_REVIEWS_PER_PLACE = 10
COMMENT_PROBABILITY = 0.7

RATINGS = [1, 2, 3, 4, 5]
RATING_WEIGHTS = [1, 2, 4, 6, 7]

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


def _build_reviews(place: Place, index: int) -> list[Review]:
    generator = Random(index)
    count = generator.randint(MIN_REVIEWS_PER_PLACE, MAX_REVIEWS_PER_PLACE)
    reviews: list[Review] = []

    for number in range(count):
        rating = generator.choices(RATINGS, weights=RATING_WEIGHTS)[0]
        comment = (
            generator.choice(COMMENTS[rating]) if generator.random() < COMMENT_PROBABILITY else None
        )
        key = f"recomendacoes-api/reviews/{place.id}/{number}"

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

    for index, seed_place in enumerate(load_places()):
        place = place_repository.find_by_id(seed_place.id)

        if place is None or review_repository.list_by_place(place.id):
            continue

        reviews = _build_reviews(place, index)

        for review in reviews:
            review_repository.save(review)

        place.recalculate_rating([review.rating for review in reviews])

        place_repository.update(place)
