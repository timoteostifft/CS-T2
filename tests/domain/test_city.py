import pytest

from recomendacoes_api.domain.entities import City
from recomendacoes_api.domain.exceptions import InvalidCityError


def test_city_is_created_with_valid_data():
    city = City(id=4314902, name="Porto Alegre", state_code="RS")

    assert city.id == 4314902
    assert city.name == "Porto Alegre"
    assert city.state_code == "RS"


def test_city_rejects_non_positive_id():
    with pytest.raises(InvalidCityError):
        City(id=0, name="Porto Alegre", state_code="RS")


def test_city_rejects_blank_name():
    with pytest.raises(InvalidCityError):
        City(id=1, name=" ", state_code="RS")


def test_city_rejects_blank_state_code():
    with pytest.raises(InvalidCityError):
        City(id=1, name="Porto Alegre", state_code="")
