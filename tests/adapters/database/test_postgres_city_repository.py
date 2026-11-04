from recomendacoes_api.adapters.database.postgres_city_repository import (
    CityModel,
    PostgresCityRepository,
)


def seed(session_factory) -> PostgresCityRepository:
    with session_factory() as session:
        session.add_all(
            [
                CityModel(id=4314902, name="Porto Alegre", state_code="RS"),
                CityModel(id=4205407, name="Florianópolis", state_code="SC"),
                CityModel(id=4207304, name="Imbituba", state_code="SC"),
            ]
        )
        session.commit()

    return PostgresCityRepository(session_factory)


def test_list_all_without_filter_returns_every_city_ordered_by_name(session_factory):
    repository = seed(session_factory)

    names = [city.name for city in repository.list_all()]

    assert names == ["Florianópolis", "Imbituba", "Porto Alegre"]


def test_list_all_filters_by_state_code(session_factory):
    repository = seed(session_factory)

    cities = repository.list_all("SC")

    assert [city.name for city in cities] == ["Florianópolis", "Imbituba"]
    assert {city.state_code for city in cities} == {"SC"}


def test_list_all_of_unknown_state_returns_empty_list(session_factory):
    repository = seed(session_factory)

    assert repository.list_all("XX") == []


def test_exists_by_id_tells_whether_the_city_exists(session_factory):
    repository = seed(session_factory)

    assert repository.exists_by_id(4314902) is True
    assert repository.exists_by_id(1) is False
