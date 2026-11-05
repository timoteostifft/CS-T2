from uuid import UUID

from recomendacoes_api.domain.exceptions import InvalidTokenError

PREFIX = "token:"


class MockTokenService:
    def issue(self, user_id: UUID) -> str:
        return f"{PREFIX}{user_id}"

    def read_subject(self, token: str) -> UUID:
        if not token.startswith(PREFIX):
            raise InvalidTokenError("Authentication token is invalid or expired")

        return UUID(token.removeprefix(PREFIX))
