from typing import Protocol
from uuid import UUID


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, password: str, password_hash: str) -> bool: ...


class TokenService(Protocol):
    def issue(self, user_id: UUID) -> str: ...

    def read_subject(self, token: str) -> UUID: ...
