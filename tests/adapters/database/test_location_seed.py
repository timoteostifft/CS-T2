from recomendacoes_api.adapters.database.location_seed import load_locations


def test_load_locations_returns_all_brazilian_states_and_cities():
    states, cities = load_locations()

    assert len(states) == 27
    assert len(cities) == 5571
    assert {city.state_code for city in cities} == {state.code for state in states}
    assert len({city.id for city in cities}) == len(cities)
