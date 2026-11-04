from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import get_list_states_use_case
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import ListStatesUseCase
from recomendacoes_api.domain.entities import State
from tests.adapters.database.mock_state_repository import MockStateRepository

STATES = [State(code="RS", name="Rio Grande do Sul")]


def list_states(states: list[State]):
    use_case = ListStatesUseCase(MockStateRepository(states))
    app.dependency_overrides[get_list_states_use_case] = lambda: use_case

    response = TestClient(app).get("/api/v1/states")

    app.dependency_overrides.clear()

    return response


def test_list_states_returns_states_as_json():
    response = list_states(STATES)

    assert response.status_code == 200
    assert response.json() == [{"code": "RS", "name": "Rio Grande do Sul"}]
