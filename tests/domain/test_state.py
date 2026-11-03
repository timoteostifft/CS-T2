import pytest

from recomendacoes_api.domain.entities import State
from recomendacoes_api.domain.exceptions import InvalidStateError


def test_state_is_created_with_valid_data():
    state = State(code="RS", name="Rio Grande do Sul")

    assert state.code == "RS"
    assert state.name == "Rio Grande do Sul"


@pytest.mark.parametrize("code", ["", "R", "RSS", "rs", "R1"])
def test_state_rejects_invalid_code(code):
    with pytest.raises(InvalidStateError):
        State(code=code, name="Rio Grande do Sul")


def test_state_rejects_blank_name():
    with pytest.raises(InvalidStateError):
        State(code="RS", name="  ")
