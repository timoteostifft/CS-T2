from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from recomendacoes_api.domain.exceptions import DomainError, InvalidPlaceError


async def invalid_place_error_handler(request: Request, exc: InvalidPlaceError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "bad_request", "message": str(exc)},
    )


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "bad_request", "message": str(exc)},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(InvalidPlaceError, invalid_place_error_handler)
    app.add_exception_handler(DomainError, domain_error_handler)
