from typing import Annotated

from fastapi import APIRouter, Depends, status

from recomendacoes_api.adapters.rest.dependencies import (
    get_current_user,
    get_login_user_use_case,
    get_register_user_use_case,
)
from recomendacoes_api.adapters.rest.schemas import (
    HealthResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from recomendacoes_api.application.use_cases import LoginUserUseCase, RegisterUserUseCase
from recomendacoes_api.domain.entities import User

auth_router = APIRouter(prefix="/auth", tags=["auth"])
health_router = APIRouter(prefix="/health", tags=["health"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_user_use_case)],
) -> UserResponse:
    user = use_case.execute(name=request.name, email=request.email, password=request.password)

    return UserResponse.from_entity(user)


@auth_router.post("/login")
def login(
    request: LoginRequest,
    use_case: Annotated[LoginUserUseCase, Depends(get_login_user_use_case)],
) -> TokenResponse:
    token = use_case.execute(email=request.email, password=request.password)

    return TokenResponse.from_token(token)


@auth_router.get("/me")
def me(user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return UserResponse.from_entity(user)


@health_router.get("")
def health() -> HealthResponse:
    return HealthResponse()
