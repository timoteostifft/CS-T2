from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import get_list_cities_use_case
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import ListCitiesUseCase
from recomendacoes_api.domain.entities import City
from tests.adapters.database.mock_city_repository import MockCityRepository

CITIES = [City(id=4314902, name="Porto Alegre", state_code="RS")]


def list_cities(cities: list[City], params: dict | None = None):
    use_case = ListCitiesUseCase(MockCityRepository(cities))
    app.dependency_overrides[get_list_cities_use_case] = lambda: use_case

    response = TestClient(app).get("/api/v1/cities", params=params)

    app.dependency_overrides.clear()

    return response


def test_list_cities_without_filter_returns_all_cities():
    response = list_cities(CITIES)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_cities_filtered_by_state_returns_cities_as_json():
    response = list_cities(CITIES, {"state_code": "RS"})

    assert response.status_code == 200
    assert response.json() == [{"id": 4314902, "name": "Porto Alegre", "state_code": "RS"}]


def test_list_cities_of_unknown_state_returns_empty_list():
    response = list_cities(CITIES, {"state_code": "XX"})

    assert response.status_code == 200
    assert response.json() == []
