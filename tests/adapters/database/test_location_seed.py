from recomendacoes_api.adapters.database.location_seed import load_locations, seed_locations
from recomendacoes_api.adapters.database.postgres_city_repository import PostgresCityRepository
from recomendacoes_api.adapters.database.postgres_state_repository import PostgresStateRepository


def test_load_locations_returns_all_brazilian_states_and_cities():
    states, cities = load_locations()

    assert len(states) == 27
    assert len(cities) == 5571
    assert {city.state_code for city in cities} == {state.code for state in states}
    assert len({city.id for city in cities}) == len(cities)


def test_seed_locations_populates_states_and_cities(session_factory):
    seed_locations(session_factory)

    assert len(PostgresStateRepository(session_factory).list_all()) == 27
    assert len(PostgresCityRepository(session_factory).list_all()) == 5571


def test_seed_locations_is_idempotent(session_factory):
    seed_locations(session_factory)
    seed_locations(session_factory)

    assert len(PostgresStateRepository(session_factory).list_all()) == 27
    assert len(PostgresCityRepository(session_factory).list_all()) == 5571
