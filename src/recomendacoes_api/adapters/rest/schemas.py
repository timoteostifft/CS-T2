from uuid import UUID

from pydantic import BaseModel, Field

from dynamic_ranker import RankedItem
from recomendacoes_api.domain.entities import Place


class PlaceResponse(BaseModel):
    id: UUID
    name: str
    category: str
    rating: float
    cost: float
    popularity: float

    @staticmethod
    def from_entity(place: Place) -> "PlaceResponse":
        return PlaceResponse(
            id=place.id,
            name=place.name,
            category=place.category,
            rating=place.rating,
            cost=place.cost,
            popularity=place.popularity,
        )


class PaginatedPlacesResponse(BaseModel):
    total: int
    items: list[PlaceResponse]


class PlaceCreate(BaseModel):
    name: str = Field(..., examples=["Torre de Belém"])
    category: str = Field(..., examples=["Monumento"])
    rating: float = Field(..., examples=[4.7])
    cost: float = Field(..., examples=[3.0])
    popularity: float = Field(..., examples=[9.5])


class PlaceUpdate(BaseModel):
    name: str | None = Field(default=None, examples=["Torre de Belém (Atualizado)"])
    category: str | None = Field(default=None, examples=["Património Mundial"])
    rating: float | None = Field(default=None, examples=[4.9])
    cost: float | None = Field(default=None, examples=[3.0])
    popularity: float | None = Field(default=None, examples=[9.8])


class PlaceRanked(BaseModel):
    id: UUID
    name: str
    category: str
    rating: float
    cost: float
    popularity: float
    score_final: float

    @staticmethod
    def from_ranked_item(ranked: RankedItem[Place]) -> "PlaceRanked":
        return PlaceRanked(
            id=ranked.item.id,
            name=ranked.item.name,
            category=ranked.item.category,
            rating=ranked.item.rating,
            cost=ranked.item.cost,
            popularity=ranked.item.popularity,
            score_final=ranked.score_final,
        )


class RankWeightsPayload(BaseModel):
    weights: dict[str, float] = Field(
        ...,
        examples=[{"rating": 0.6, "cost": -0.3, "popularity": 0.1}],
    )


class ErrorResponse(BaseModel):
    code: int
    message: str
