from recomendacoes_api.adapters.database.place_seed import load_places, seed_places
from recomendacoes_api.adapters.database.postgres_place_repository import PostgresPlaceRepository
from recomendacoes_api.domain.entities import Place


def test_load_places_returns_at_least_thirty_unique_places():
    places = load_places()

    assert len(places) >= 30
    assert len({place.id for place in places}) == len(places)
    assert len({place.name for place in places}) == len(places)


def test_load_places_is_deterministic():
    first_ids = [place.id for place in load_places()]

    second_ids = [place.id for place in load_places()]

    assert first_ids == second_ids


def test_seed_places_populates_places(session_factory):
    seed_places(session_factory)

    assert PostgresPlaceRepository(session_factory).count_all() == len(load_places())


def test_seed_places_is_idempotent(session_factory):
    seed_places(session_factory)
    seed_places(session_factory)

    assert PostgresPlaceRepository(session_factory).count_all() == len(load_places())


def test_seed_places_skips_when_places_already_exist(session_factory):
    repository = PostgresPlaceRepository(session_factory)
    repository.save(Place.create(name="Existing", category="beach", city_id=1, cost=0))

    seed_places(session_factory)

    assert repository.count_all() == 1
