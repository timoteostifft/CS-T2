from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import (
    get_get_current_user_use_case,
    get_login_user_use_case,
    get_register_user_use_case,
)
from recomendacoes_api.app import app
from recomendacoes_api.application.use_cases import (
    GetCurrentUserUseCase,
    LoginUserUseCase,
    RegisterUserUseCase,
)
from recomendacoes_api.domain.entities import User
from tests.adapters.database.mock_user_repository import MockUserRepository
from tests.adapters.security.mock_password_hasher import MockPasswordHasher
from tests.adapters.security.mock_token_service import MockTokenService

VALID_BODY = {"name": "Ana", "email": "ana@example.com", "password": "secret123"}


def make_user() -> User:
    return User.create(name="Ana", email="ana@example.com", password_hash="hashed:secret123")


def register(body: dict, users: list[User] | None = None):
    repository = MockUserRepository(users)
    app.dependency_overrides[get_register_user_use_case] = lambda: RegisterUserUseCase(
        repository, MockPasswordHasher()
    )

    response = TestClient(app).post("/api/v1/auth/register", json=body)

    app.dependency_overrides.clear()

    return response


def login(body: dict, users: list[User] | None = None):
    app.dependency_overrides[get_login_user_use_case] = lambda: LoginUserUseCase(
        MockUserRepository(users), MockPasswordHasher(), MockTokenService()
    )

    response = TestClient(app).post("/api/v1/auth/login", json=body)

    app.dependency_overrides.clear()

    return response


def me(users: list[User], headers: dict | None = None):
    app.dependency_overrides[get_get_current_user_use_case] = lambda: GetCurrentUserUseCase(
        MockUserRepository(users), MockTokenService()
    )

    response = TestClient(app).get("/api/v1/auth/me", headers=headers)

    app.dependency_overrides.clear()

    return response


def test_register_returns_201_without_the_password():
    response = register(VALID_BODY)

    body = response.json()

    assert response.status_code == 201
    assert body["name"] == "Ana"
    assert body["email"] == "ana@example.com"
    assert "id" in body
    assert "password" not in body
    assert "password_hash" not in body


def test_register_with_a_registered_email_returns_409():
    response = register(VALID_BODY, [make_user()])

    assert response.status_code == 409
    assert response.json()["error"] == "conflict"


def test_register_with_a_short_password_returns_422():
    assert register({**VALID_BODY, "password": "short"}).status_code == 422


def test_register_with_an_invalid_email_returns_422():
    assert register({**VALID_BODY, "email": "not-an-email"}).status_code == 422


def test_login_returns_a_bearer_token():
    user = make_user()

    response = login({"email": "ana@example.com", "password": "secret123"}, [user])

    assert response.status_code == 200
    assert response.json() == {
        "access_token": MockTokenService().issue(user.id),
        "token_type": "bearer",
    }


def test_login_with_a_wrong_password_returns_401():
    response = login({"email": "ana@example.com", "password": "wrong-pass"}, [make_user()])

    assert response.status_code == 401
    assert response.json()["error"] == "unauthorized"


def test_me_returns_the_authenticated_user():
    user = make_user()
    headers = {"Authorization": f"Bearer {MockTokenService().issue(user.id)}"}

    response = me([user], headers)

    assert response.status_code == 200
    assert response.json() == {"id": str(user.id), "name": "Ana", "email": "ana@example.com"}


def test_me_without_a_token_returns_401():
    assert me([make_user()]).status_code == 401


def test_me_with_an_invalid_token_returns_401():
    assert me([make_user()], {"Authorization": "Bearer garbage"}).status_code == 401
