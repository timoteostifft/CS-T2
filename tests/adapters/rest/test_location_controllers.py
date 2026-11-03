from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import (
    get_list_cities_use_case,
    get_list_states_use_case,
)
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import ListCitiesUseCase, ListStatesUseCase
from recomendacoes_api.domain.entities import City, State
from tests.adapters.database.mock_city_repository import MockCityRepository
from tests.adapters.database.mock_state_repository import MockStateRepository

STATES = [State(code="RS", name="Rio Grande do Sul")]
CITIES = [City(id=4314902, name="Porto Alegre", state_code="RS")]


def test_list_states_returns_states_as_json():
    use_case = ListStatesUseCase(MockStateRepository(STATES))
    app.dependency_overrides[get_list_states_use_case] = lambda: use_case

    response = TestClient(app).get("/states")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [{"code": "RS", "name": "Rio Grande do Sul"}]


def test_list_cities_without_filter_returns_all_cities():
    use_case = ListCitiesUseCase(MockCityRepository(CITIES))
    app.dependency_overrides[get_list_cities_use_case] = lambda: use_case

    response = TestClient(app).get("/cities")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_cities_filtered_by_state_returns_cities_as_json():
    use_case = ListCitiesUseCase(MockCityRepository(CITIES))
    app.dependency_overrides[get_list_cities_use_case] = lambda: use_case

    response = TestClient(app).get("/cities", params={"state_code": "RS"})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [{"id": 4314902, "name": "Porto Alegre", "state_code": "RS"}]


def test_list_cities_of_unknown_state_returns_empty_list():
    use_case = ListCitiesUseCase(MockCityRepository(CITIES))
    app.dependency_overrides[get_list_cities_use_case] = lambda: use_case

    response = TestClient(app).get("/cities", params={"state_code": "XX"})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == []
