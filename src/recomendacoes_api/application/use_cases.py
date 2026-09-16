from recomendacoes_api.domain.entities import Place
from recomendacoes_api.ports.repositories import PlaceRepository


class ListPlacesUseCase:
    def __init__(self, place_repository: PlaceRepository) -> None:
        self._place_repository = place_repository

    def execute(self) -> list[Place]:
        return self._place_repository.list_all()
