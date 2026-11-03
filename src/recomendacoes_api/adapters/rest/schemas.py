from uuid import UUID

from pydantic import BaseModel

from recomendacoes_api.domain.entities import City, Place, State


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


class StateResponse(BaseModel):
    code: str
    name: str

    @staticmethod
    def from_entity(state: State) -> "StateResponse":
        return StateResponse(code=state.code, name=state.name)


class CityResponse(BaseModel):
    id: int
    name: str
    state_code: str

    @staticmethod
    def from_entity(city: City) -> "CityResponse":
        return CityResponse(id=city.id, name=city.name, state_code=city.state_code)
