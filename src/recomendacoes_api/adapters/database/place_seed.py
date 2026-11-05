import json
from importlib.resources import files
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy.orm import Session, sessionmaker

from recomendacoes_api.adapters.database.postgres_place_repository import PostgresPlaceRepository
from recomendacoes_api.domain.entities import Place


def seed_place_id(name: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"recomendacoes-api/places/{name}")


def load_places() -> list[Place]:
    raw = files("recomendacoes_api.adapters.database").joinpath("places.json").read_text("utf-8")

    return [
        Place(
            id=seed_place_id(item["name"]),
            name=item["name"],
            category=item["category"],
            city_id=item["city_id"],
            cost=item["cost"],
        )
        for item in json.loads(raw)
    ]


def seed_places(session_factory: sessionmaker[Session]) -> None:
    repository = PostgresPlaceRepository(session_factory)

    if repository.count_all():
        return

    for place in load_places():
        repository.save(place)
