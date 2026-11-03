from recomendacoes_api.application.use_cases import ListStatesUseCase
from recomendacoes_api.domain.entities import State
from tests.adapters.database.mock_state_repository import MockStateRepository


def test_list_states_returns_states_from_repository():
    states = [State(code="RS", name="Rio Grande do Sul"), State(code="SC", name="Santa Catarina")]
    use_case = ListStatesUseCase(MockStateRepository(states))

    assert use_case.execute() == states
