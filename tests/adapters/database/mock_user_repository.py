from uuid import UUID

from recomendacoes_api.domain.entities import User


class MockUserRepository:
    def __init__(self, users: list[User] | None = None) -> None:
        self.users: list[User] = list(users or [])

    def find_by_id(self, user_id: UUID) -> User | None:
        return next((user for user in self.users if user.id == user_id), None)

    def find_by_email(self, email: str) -> User | None:
        return next((user for user in self.users if user.email == email), None)

    def list_by_ids(self, user_ids: list[UUID]) -> list[User]:
        return [user for user in self.users if user.id in user_ids]

    def save(self, user: User) -> None:
        self.users.append(user)
