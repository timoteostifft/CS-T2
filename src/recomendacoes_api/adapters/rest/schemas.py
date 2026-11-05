from collections.abc import Callable
from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from recomendacoes_api.domain.entities import MIN_PASSWORD_LENGTH, User
from recomendacoes_api.domain.pagination import DEFAULT_LIMIT, MAX_LIMIT, Page


class PaginationRequest(BaseModel):
    limit: int = Field(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT)
    offset: int = Field(0, ge=0)


class PageResponse[T](BaseModel):
    total: int
    items: list[T]

    @classmethod
    def from_page[E](cls, page: Page[E], to_response: Callable[[E], T]) -> Self:
        return cls(total=page.total, items=[to_response(item) for item in page.items])


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str

    @staticmethod
    def from_entity(user: User) -> "UserResponse":
        return UserResponse(id=user.id, name=user.name, email=user.email)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"

    @staticmethod
    def from_token(token: str) -> "TokenResponse":
        return TokenResponse(access_token=token)


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
