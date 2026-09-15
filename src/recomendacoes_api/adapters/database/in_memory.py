from recomendacoes_api.domain.entities import Place


class InMemoryPlaceRepository:
    def __init__(self) -> None:
        self._places: list[Place] = [
            Place.create(name="Praia do Rosa", city="Imbituba", category="beach"),
            Place.create(name="Pedra Furada", city="Jeriquara", category="trail"),
        ]

    def list_all(self) -> list[Place]:
        return list(self._places)
