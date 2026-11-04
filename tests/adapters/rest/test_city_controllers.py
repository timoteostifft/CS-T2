import pytest
from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import get_list_cities_use_case
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import ListCitiesUseCase
from recomendacoes_api.domain.entities import City
from tests.adapters.database.mock_city_repository import MockCityRepository

CITIES = [
    City(id=4314902, name="Porto Alegre", state_code="RS"),
    City(id=4205407, name="Florianópolis", state_code="SC"),
    City(id=4207304, name="Imbituba", state_code="SC"),
]


def list_cities(cities: list[City], params: dict | None = None):
    use_case = ListCitiesUseCase(MockCityRepository(cities))
    app.dependency_overrides[get_list_cities_use_case] = lambda: use_case

    response = TestClient(app).get("/api/v1/cities", params=params)

    app.dependency_overrides.clear()

    return response


def test_list_cities_without_filter_returns_a_page_with_every_city():
    response = list_cities(CITIES)

    assert response.status_code == 200
    assert response.json()["total"] == 3
    assert len(response.json()["items"]) == 3


def test_list_cities_filtered_by_state_returns_cities_as_json():
    response = list_cities(CITIES, {"state_code": "RS"})

    assert response.status_code == 200
    assert response.json() == {
        "total": 1,
        "items": [{"id": 4314902, "name": "Porto Alegre", "state_code": "RS"}],
    }


def test_list_cities_of_unknown_state_returns_empty_page():
    response = list_cities(CITIES, {"state_code": "XX"})

    assert response.status_code == 200
    assert response.json() == {"total": 0, "items": []}


def test_list_cities_applies_limit_and_offset_with_the_filter():
    response = list_cities(CITIES, {"state_code": "SC", "limit": 1, "offset": 1})

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert [city["name"] for city in response.json()["items"]] == ["Imbituba"]


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}])
def test_list_cities_with_invalid_pagination_returns_422(params):
    assert list_cities(CITIES, params).status_code == 422
