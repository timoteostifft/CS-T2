from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from recomendacoes_api.domain.exceptions import (
    ActivityNotFoundError,
    AlreadyCollaboratorError,
    CollaboratorNotFoundError,
    DestinationNotFoundError,
    DomainError,
    EmailAlreadyRegisteredError,
    InvalidActivityError,
    InvalidCredentialsError,
    InvalidDestinationError,
    InvalidScheduledActivityError,
    InvalidTokenError,
    InvalidTripError,
    InvalidUserError,
    ScheduledActivityNotFoundError,
    TripAccessDeniedError,
    TripNotFoundError,
)


def error_response(status_code: int, error: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": error, "code": status_code, "message": message},
    )


def invalid_user_error_handler(request: Request, exc: InvalidUserError) -> JSONResponse:
    return error_response(status.HTTP_400_BAD_REQUEST, "bad_request", str(exc))


def email_already_registered_error_handler(
    request: Request, exc: EmailAlreadyRegisteredError
) -> JSONResponse:
    return error_response(status.HTTP_409_CONFLICT, "conflict", str(exc))


def invalid_credentials_error_handler(
    request: Request, exc: InvalidCredentialsError
) -> JSONResponse:
    return error_response(status.HTTP_401_UNAUTHORIZED, "unauthorized", str(exc))


def invalid_token_error_handler(request: Request, exc: InvalidTokenError) -> JSONResponse:
    return error_response(status.HTTP_401_UNAUTHORIZED, "unauthorized", str(exc))


def invalid_trip_error_handler(request: Request, exc: InvalidTripError) -> JSONResponse:
    return error_response(status.HTTP_400_BAD_REQUEST, "bad_request", str(exc))


def trip_not_found_error_handler(request: Request, exc: TripNotFoundError) -> JSONResponse:
    return error_response(status.HTTP_404_NOT_FOUND, "not_found", str(exc))


def trip_access_denied_error_handler(request: Request, exc: TripAccessDeniedError) -> JSONResponse:
    return error_response(status.HTTP_403_FORBIDDEN, "forbidden", str(exc))


def invalid_destination_error_handler(
    request: Request, exc: InvalidDestinationError
) -> JSONResponse:
    return error_response(status.HTTP_400_BAD_REQUEST, "bad_request", str(exc))


def destination_not_found_error_handler(
    request: Request, exc: DestinationNotFoundError
) -> JSONResponse:
    return error_response(status.HTTP_404_NOT_FOUND, "not_found", str(exc))


def invalid_activity_error_handler(request: Request, exc: InvalidActivityError) -> JSONResponse:
    return error_response(status.HTTP_400_BAD_REQUEST, "bad_request", str(exc))


def activity_not_found_error_handler(request: Request, exc: ActivityNotFoundError) -> JSONResponse:
    return error_response(status.HTTP_404_NOT_FOUND, "not_found", str(exc))


def invalid_scheduled_error_handler(
    request: Request, exc: InvalidScheduledActivityError
) -> JSONResponse:
    return error_response(status.HTTP_400_BAD_REQUEST, "bad_request", str(exc))


def scheduled_not_found_error_handler(
    request: Request, exc: ScheduledActivityNotFoundError
) -> JSONResponse:
    return error_response(status.HTTP_404_NOT_FOUND, "not_found", str(exc))


def already_collaborator_error_handler(
    request: Request, exc: AlreadyCollaboratorError
) -> JSONResponse:
    return error_response(status.HTTP_409_CONFLICT, "conflict", str(exc))


def collaborator_not_found_error_handler(
    request: Request, exc: CollaboratorNotFoundError
) -> JSONResponse:
    return error_response(status.HTTP_404_NOT_FOUND, "not_found", str(exc))


def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return error_response(status.HTTP_400_BAD_REQUEST, "bad_request", str(exc))


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(InvalidUserError, invalid_user_error_handler)
    app.add_exception_handler(EmailAlreadyRegisteredError, email_already_registered_error_handler)
    app.add_exception_handler(InvalidCredentialsError, invalid_credentials_error_handler)
    app.add_exception_handler(InvalidTokenError, invalid_token_error_handler)
    app.add_exception_handler(InvalidTripError, invalid_trip_error_handler)
    app.add_exception_handler(TripNotFoundError, trip_not_found_error_handler)
    app.add_exception_handler(TripAccessDeniedError, trip_access_denied_error_handler)
    app.add_exception_handler(InvalidDestinationError, invalid_destination_error_handler)
    app.add_exception_handler(DestinationNotFoundError, destination_not_found_error_handler)
    app.add_exception_handler(InvalidActivityError, invalid_activity_error_handler)
    app.add_exception_handler(ActivityNotFoundError, activity_not_found_error_handler)
    app.add_exception_handler(InvalidScheduledActivityError, invalid_scheduled_error_handler)
    app.add_exception_handler(ScheduledActivityNotFoundError, scheduled_not_found_error_handler)
    app.add_exception_handler(AlreadyCollaboratorError, already_collaborator_error_handler)
    app.add_exception_handler(CollaboratorNotFoundError, collaborator_not_found_error_handler)
    app.add_exception_handler(DomainError, domain_error_handler)
