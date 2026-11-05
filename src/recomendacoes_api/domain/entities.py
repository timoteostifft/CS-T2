from dataclasses import dataclass, field
from uuid import UUID, uuid4

from recomendacoes_api.domain.exceptions import InvalidUserError

MIN_PASSWORD_LENGTH = 8


@dataclass
class User:
    name: str
    email: str
    password_hash: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidUserError("User name must not be empty")
        if "@" not in self.email.strip("@"):
            raise InvalidUserError("User email is invalid")
        if not self.password_hash:
            raise InvalidUserError("User password hash must not be empty")

    @staticmethod
    def create(name: str, email: str, password_hash: str) -> "User":
        return User(
            name=name.strip(),
            email=User.normalize_email(email),
            password_hash=password_hash,
        )

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()
