from uuid import uuid4

import pytest

from recomendacoes_api.adapters.security.jwt_token_service import JwtTokenService
from recomendacoes_api.domain.exceptions import InvalidTokenError

SECRET = "s" * 32
OTHER_SECRET = "o" * 32


def test_read_subject_returns_the_issued_user_id():
    service = JwtTokenService(SECRET, 60)
    user_id = uuid4()

    assert service.read_subject(service.issue(user_id)) == user_id


def test_read_subject_rejects_a_token_signed_with_another_secret():
    token = JwtTokenService(OTHER_SECRET, 60).issue(uuid4())

    with pytest.raises(InvalidTokenError):
        JwtTokenService(SECRET, 60).read_subject(token)


def test_read_subject_rejects_an_expired_token():
    service = JwtTokenService(SECRET, -1)

    with pytest.raises(InvalidTokenError):
        service.read_subject(service.issue(uuid4()))


def test_read_subject_rejects_garbage():
    with pytest.raises(InvalidTokenError):
        JwtTokenService(SECRET, 60).read_subject("garbage")
