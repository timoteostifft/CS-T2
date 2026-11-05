from typing import Protocol
from uuid import UUID

from recomendacoes_api.domain.entities import User


class UserRepository(Protocol):
    def find_by_id(self, user_id: UUID) -> User | None: ...

    def find_by_email(self, email: str) -> User | None: ...

    def save(self, user: User) -> None: ...
