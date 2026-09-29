from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from recomendacoes_api.domain.exceptions import (
    DomainError,
    InvalidPlaceError,
    InvalidRankWeightsError,
    PlaceNotFoundError,
)


class UnauthorizedError(Exception):
    pass


async def invalid_place_error_handler(request: Request, exc: InvalidPlaceError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"code": 400, "message": str(exc)},
    )


async def invalid_rank_weights_error_handler(
    request: Request, exc: InvalidRankWeightsError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"code": 400, "message": str(exc)},
    )


async def place_not_found_error_handler(request: Request, exc: PlaceNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"code": 404, "message": str(exc)},
    )


async def unauthorized_error_handler(request: Request, exc: UnauthorizedError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"code": 401, "message": str(exc) or "Token JWT ausente, inválido ou expirado."},
    )


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"code": 400, "message": str(exc)},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(InvalidPlaceError, invalid_place_error_handler)
    app.add_exception_handler(InvalidRankWeightsError, invalid_rank_weights_error_handler)
    app.add_exception_handler(PlaceNotFoundError, place_not_found_error_handler)
    app.add_exception_handler(UnauthorizedError, unauthorized_error_handler)
    app.add_exception_handler(DomainError, domain_error_handler)
