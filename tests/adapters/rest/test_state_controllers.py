import pytest
from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import get_list_states_use_case
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import ListStatesUseCase
from recomendacoes_api.domain.entities import State
from tests.adapters.database.mock_state_repository import MockStateRepository

STATES = [
    State(code="RS", name="Rio Grande do Sul"),
    State(code="SC", name="Santa Catarina"),
]


def list_states(states: list[State], params: dict | None = None):
    use_case = ListStatesUseCase(MockStateRepository(states))
    app.dependency_overrides[get_list_states_use_case] = lambda: use_case

    response = TestClient(app).get("/api/v1/states", params=params)

    app.dependency_overrides.clear()

    return response


def test_list_states_returns_a_page_as_json():
    response = list_states(STATES)

    assert response.status_code == 200
    assert response.json() == {
        "total": 2,
        "items": [
            {"code": "RS", "name": "Rio Grande do Sul"},
            {"code": "SC", "name": "Santa Catarina"},
        ],
    }


def test_list_states_applies_limit_and_offset():
    response = list_states(STATES, {"limit": 1, "offset": 1})

    assert response.status_code == 200
    assert response.json() == {"total": 2, "items": [{"code": "SC", "name": "Santa Catarina"}]}


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}])
def test_list_states_with_invalid_pagination_returns_422(params):
    assert list_states(STATES, params).status_code == 422
