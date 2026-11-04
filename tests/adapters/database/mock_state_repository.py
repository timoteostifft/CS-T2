from recomendacoes_api.domain.entities import State


class MockStateRepository:
    def __init__(self, states: list[State] | None = None) -> None:
        self._states = states or []

    def list_all(self, limit: int | None = None, offset: int = 0) -> list[State]:
        end = None if limit is None else offset + limit

        return self._states[offset:end]

    def count_all(self) -> int:
        return len(self._states)
