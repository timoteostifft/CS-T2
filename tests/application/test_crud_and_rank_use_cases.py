from uuid import uuid4

import pytest

from recomendacoes_api.application.use_cases import (
    DeletePlaceUseCase,
    GetPlaceByIdUseCase,
    RankPlacesUseCase,
    UpdatePlaceUseCase,
)
from recomendacoes_api.domain.entities import Place
from recomendacoes_api.domain.exceptions import (
    InvalidRankWeightsError,
    PlaceNotFoundError,
)
from tests.adapters.database.mock_place_repository import MockPlaceRepository


def test_get_place_by_id_returns_place_when_found():
    place = Place.create("Torre", "Monumento", 4.5, 2.0, 10.0)
    repo = MockPlaceRepository([place])
    use_case = GetPlaceByIdUseCase(repo)

    result = use_case.execute(place.id)

    assert result == place


def test_get_place_by_id_raises_not_found_when_missing():
    repo = MockPlaceRepository()
    use_case = GetPlaceByIdUseCase(repo)

    with pytest.raises(PlaceNotFoundError):
        use_case.execute(uuid4())


def test_update_place_updates_fields_successfully():
    place = Place.create("Torre", "Monumento", 4.5, 2.0, 10.0)
    repo = MockPlaceRepository([place])
    use_case = UpdatePlaceUseCase(repo)

    updated = use_case.execute(
        id=place.id,
        name="Torre de Belém (Atualizado)",
        category="Património",
        rating=4.9,
    )

    assert updated.name == "Torre de Belém (Atualizado)"
    assert updated.category == "Património"
    assert updated.rating == 4.9
    assert updated.cost == 2.0
    assert updated.popularity == 10.0


def test_update_place_raises_not_found_when_missing():
    repo = MockPlaceRepository()
    use_case = UpdatePlaceUseCase(repo)

    with pytest.raises(PlaceNotFoundError):
        use_case.execute(id=uuid4(), name="Novo")


def test_delete_place_removes_from_repository():
    place = Place.create("Torre", "Monumento", 4.5, 2.0, 10.0)
    repo = MockPlaceRepository([place])
    use_case = DeletePlaceUseCase(repo)

    use_case.execute(place.id)

    assert len(repo.list_all()) == 0


def test_delete_place_raises_not_found_when_missing():
    repo = MockPlaceRepository()
    use_case = DeletePlaceUseCase(repo)

    with pytest.raises(PlaceNotFoundError):
        use_case.execute(uuid4())


def test_rank_places_returns_ordered_results():
    place1 = Place.create("Lugar Barato", "Natureza", rating=4.0, cost=1.0, popularity=5.0)
    place2 = Place.create("Lugar Popular", "Praia", rating=4.8, cost=5.0, popularity=10.0)
    repo = MockPlaceRepository([place1, place2])
    use_case = RankPlacesUseCase(repo)

    # Prioritizing low cost: cost * (-1.0) + rating * 1.0
    # place1: -1.0 + 4.0 = 3.0
    # place2: -5.0 + 4.8 = -0.2
    ranked = use_case.execute(weights={"cost": -1.0, "rating": 1.0}, limit=2)

    assert len(ranked) == 2
    assert ranked[0].item.name == "Lugar Barato"
    assert ranked[0].score_final == 3.0
    assert ranked[1].item.name == "Lugar Popular"
    assert ranked[1].score_final == -0.2


def test_rank_places_with_invalid_weights_raises_invalid_rank_weights_error():
    repo = MockPlaceRepository([Place.create("Lugar", "Praia", 4.0, 1.0, 5.0)])
    use_case = RankPlacesUseCase(repo)

    with pytest.raises(InvalidRankWeightsError):
        use_case.execute(weights={"campo_inexistente": 1.0})
