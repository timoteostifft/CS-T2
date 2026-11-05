import pytest

from recomendacoes_api.domain.entities import User
from recomendacoes_api.domain.exceptions import InvalidUserError


def test_create_normalizes_name_and_email():
    user = User.create(name="  Ana  ", email="  Ana@Example.COM ", password_hash="hash")

    assert user.name == "Ana"
    assert user.email == "ana@example.com"


def test_create_generates_distinct_ids():
    first = User.create(name="Ana", email="ana@example.com", password_hash="hash")
    second = User.create(name="Ana", email="ana@example.com", password_hash="hash")

    assert first.id != second.id


@pytest.mark.parametrize("name", ["", "   "])
def test_empty_name_is_rejected(name):
    with pytest.raises(InvalidUserError):
        User.create(name=name, email="ana@example.com", password_hash="hash")


@pytest.mark.parametrize("email", ["", "ana", "@", "@example.com"])
def test_invalid_email_is_rejected(email):
    with pytest.raises(InvalidUserError):
        User.create(name="Ana", email=email, password_hash="hash")


def test_empty_password_hash_is_rejected():
    with pytest.raises(InvalidUserError):
        User.create(name="Ana", email="ana@example.com", password_hash="")
