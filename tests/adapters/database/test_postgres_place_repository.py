from uuid import uuid4

from recomendacoes_api.adapters.database.postgres_place_repository import PostgresPlaceRepository
from recomendacoes_api.domain.entities import Place


def build_place(name: str = "Praia do Rosa", **overrides) -> Place:
    data = {"category": "beach", "city_id": 4207304, "rating": 4.5, "cost": 30.0}

    return Place.create(name=name, **{**data, **overrides})


def test_save_then_find_by_id_returns_the_place(session_factory):
    repository = PostgresPlaceRepository(session_factory)
    place = build_place()

    repository.save(place)

    assert repository.find_by_id(place.id) == place


def test_find_by_id_returns_none_when_missing(session_factory):
    repository = PostgresPlaceRepository(session_factory)

    assert repository.find_by_id(uuid4()) is None


def test_list_all_returns_places_ordered_by_name(session_factory):
    repository = PostgresPlaceRepository(session_factory)
    repository.save(build_place("Praia da Silveira"))
    repository.save(build_place("Farol de Santa Marta"))

    names = [place.name for place in repository.list_all()]

    assert names == ["Farol de Santa Marta", "Praia da Silveira"]


def test_list_all_applies_limit_and_offset(session_factory):
    repository = PostgresPlaceRepository(session_factory)

    for name in ["A", "B", "C", "D"]:
        repository.save(build_place(name))

    names = [place.name for place in repository.list_all(limit=2, offset=1)]

    assert names == ["B", "C"]


def test_count_all_returns_the_number_of_places(session_factory):
    repository = PostgresPlaceRepository(session_factory)

    assert repository.count_all() == 0

    repository.save(build_place("A"))
    repository.save(build_place("B"))

    assert repository.count_all() == 2


def test_update_changes_the_stored_place(session_factory):
    repository = PostgresPlaceRepository(session_factory)
    place = build_place()
    repository.save(place)

    place.rating = 3.0
    place.cost = 10.0
    repository.update(place)

    stored = repository.find_by_id(place.id)

    assert stored.rating == 3.0
    assert stored.cost == 10.0


def test_delete_removes_the_place(session_factory):
    repository = PostgresPlaceRepository(session_factory)
    place = build_place()
    repository.save(place)

    repository.delete(place.id)

    assert repository.find_by_id(place.id) is None


def test_delete_of_missing_place_does_nothing(session_factory):
    repository = PostgresPlaceRepository(session_factory)

    repository.delete(uuid4())

    assert repository.count_all() == 0
