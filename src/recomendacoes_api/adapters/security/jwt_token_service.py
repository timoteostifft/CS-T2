from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from recomendacoes_api.domain.exceptions import InvalidTokenError

ALGORITHM = "HS256"


class JwtTokenService:
    def __init__(self, secret: str, expire_minutes: int) -> None:
        self._secret = secret
        self._expire_minutes = expire_minutes

    def issue(self, user_id: UUID) -> str:
        expires_at = datetime.now(UTC) + timedelta(minutes=self._expire_minutes)

        return jwt.encode({"sub": str(user_id), "exp": expires_at}, self._secret, ALGORITHM)

    def read_subject(self, token: str) -> UUID:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[ALGORITHM])

            return UUID(payload["sub"])
        except (jwt.PyJWTError, KeyError, ValueError) as error:
            raise InvalidTokenError("Authentication token is invalid or expired") from error
