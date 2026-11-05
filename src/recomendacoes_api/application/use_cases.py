from recomendacoes_api.domain.entities import MIN_PASSWORD_LENGTH, User
from recomendacoes_api.domain.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidTokenError,
    InvalidUserError,
)
from recomendacoes_api.ports.repositories import UserRepository
from recomendacoes_api.ports.security import PasswordHasher, TokenService


class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    def execute(self, name: str, email: str, password: str) -> User:
        if len(password) < MIN_PASSWORD_LENGTH:
            raise InvalidUserError(f"Password must have at least {MIN_PASSWORD_LENGTH} characters")

        user = User.create(
            name=name, email=email, password_hash=self._password_hasher.hash(password)
        )

        if self._user_repository.find_by_email(user.email) is not None:
            raise EmailAlreadyRegisteredError(f"Email {user.email} is already registered")

        self._user_repository.save(user)

        return user


class LoginUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_service = token_service

    def execute(self, email: str, password: str) -> str:
        user = self._user_repository.find_by_email(User.normalize_email(email))

        if user is None or not self._password_hasher.verify(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        return self._token_service.issue(user.id)


class GetCurrentUserUseCase:
    def __init__(self, user_repository: UserRepository, token_service: TokenService) -> None:
        self._user_repository = user_repository
        self._token_service = token_service

    def execute(self, token: str | None) -> User:
        if token is None:
            raise InvalidTokenError("Authentication token is missing")

        user = self._user_repository.find_by_id(self._token_service.read_subject(token))

        if user is None:
            raise InvalidTokenError("Authentication token does not match any user")

        return user
