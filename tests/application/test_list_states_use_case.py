from recomendacoes_api.application.use_cases import ListStatesUseCase
from recomendacoes_api.domain.entities import State
from tests.adapters.database.mock_state_repository import MockStateRepository

STATES = [
    State(code="RS", name="Rio Grande do Sul"),
    State(code="SC", name="Santa Catarina"),
    State(code="PR", name="Paraná"),
]


def test_list_states_returns_a_page_with_the_states_and_the_total():
    use_case = ListStatesUseCase(MockStateRepository(STATES))

    page = use_case.execute()

    assert page.items == STATES
    assert page.total == 3


def test_list_states_applies_limit_and_offset_but_keeps_the_full_total():
    use_case = ListStatesUseCase(MockStateRepository(STATES))

    page = use_case.execute(limit=1, offset=1)

    assert page.items == [STATES[1]]
    assert page.total == 3
