from uuid import UUID

from pydantic import BaseModel

from recomendacoes_api.domain.entities import Place


class PlaceResponse(BaseModel):
    id: UUID
    name: str
    city: str
    category: str

    @staticmethod
    def from_entity(place: Place) -> "PlaceResponse":
        return PlaceResponse(
            id=place.id,
            name=place.name,
            city=place.city,
            category=place.category,
        )
