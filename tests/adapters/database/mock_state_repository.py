from recomendacoes_api.domain.entities import State


class MockStateRepository:
    def __init__(self, states: list[State] | None = None) -> None:
        self._states = states or []

    def list_all(self) -> list[State]:
        return self._states
