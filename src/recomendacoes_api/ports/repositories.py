from typing import Protocol

from recomendacoes_api.domain.entities import Place


class PlaceRepository(Protocol):
    def list_all(self) -> list[Place]: ...
