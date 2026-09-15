from recomendacoes_api.domain.entities import Place


class MockPlaceRepository:
    def __init__(self, places: list[Place] | None = None) -> None:
        self._places = places or []

    def list_all(self) -> list[Place]:
        return self._places
