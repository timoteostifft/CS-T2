import json
from importlib.resources import files

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from recomendacoes_api.adapters.database.postgres_city_repository import CityModel
from recomendacoes_api.adapters.database.postgres_state_repository import StateModel
from recomendacoes_api.domain.entities import City, State


def load_locations() -> tuple[list[State], list[City]]:
    raw = files("recomendacoes_api.adapters.database").joinpath("locations.json").read_text("utf-8")

    states: list[State] = []
    cities: list[City] = []

    for item in json.loads(raw):
        states.append(State(code=item["code"], name=item["name"]))
        cities.extend(
            City(id=city["id"], name=city["name"], state_code=item["code"])
            for city in item["cities"]
        )

    return states, cities


def seed_locations(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        if session.scalar(select(func.count()).select_from(StateModel)):
            return

        states, cities = load_locations()

        session.add_all(StateModel(code=s.code, name=s.name) for s in states)
        session.add_all(CityModel(id=c.id, name=c.name, state_code=c.state_code) for c in cities)

        session.commit()
