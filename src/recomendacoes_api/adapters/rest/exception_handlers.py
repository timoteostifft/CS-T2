from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from recomendacoes_api.domain.exceptions import (
    DomainError,
    InvalidPlaceError,
    PlaceNotFoundError,
)


def error_response(status_code: int, error: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": error, "code": status_code, "message": message},
    )


async def invalid_place_error_handler(request: Request, exc: InvalidPlaceError) -> JSONResponse:
    return error_response(status.HTTP_400_BAD_REQUEST, "bad_request", str(exc))


async def place_not_found_error_handler(request: Request, exc: PlaceNotFoundError) -> JSONResponse:
    return error_response(status.HTTP_404_NOT_FOUND, "not_found", str(exc))


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return error_response(status.HTTP_400_BAD_REQUEST, "bad_request", str(exc))


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(InvalidPlaceError, invalid_place_error_handler)
    app.add_exception_handler(PlaceNotFoundError, place_not_found_error_handler)
    app.add_exception_handler(DomainError, domain_error_handler)
