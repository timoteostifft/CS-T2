from fastapi.testclient import TestClient

from recomendacoes_api.adapters.rest.dependencies import get_login_user_use_case
from recomendacoes_api.app import app
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

LOGIN_BODY = {"email": "ana@example.com", "password": "secret123"}


def raising(error: Exception):
    class RaisingUseCase:
        def execute(self, *args, **kwargs):
            raise error

    return RaisingUseCase()


def login_with(error: Exception):
    app.dependency_overrides[get_login_user_use_case] = lambda: raising(error)

    response = TestClient(app).post("/api/v1/auth/login", json=LOGIN_BODY)

    app.dependency_overrides.clear()

    return response


def test_invalid_user_error_is_translated_to_400():
    response = login_with(InvalidUserError("User name must not be empty"))

    assert response.status_code == 400
    assert response.json() == {
        "error": "bad_request",
        "code": 400,
        "message": "User name must not be empty",
    }


def test_email_already_registered_error_is_translated_to_409():
    response = login_with(EmailAlreadyRegisteredError("Email already registered"))

    assert response.status_code == 409
    assert response.json() == {
        "error": "conflict",
        "code": 409,
        "message": "Email already registered",
    }


def test_invalid_credentials_error_is_translated_to_401():
    response = login_with(InvalidCredentialsError("Invalid email or password"))

    assert response.status_code == 401
    assert response.json() == {
        "error": "unauthorized",
        "code": 401,
        "message": "Invalid email or password",
    }


def test_invalid_token_error_is_translated_to_401():
    response = login_with(InvalidTokenError("Token is invalid"))

    assert response.status_code == 401
    assert response.json() == {"error": "unauthorized", "code": 401, "message": "Token is invalid"}


def test_invalid_trip_error_is_translated_to_400():
    response = login_with(InvalidTripError("Trip name must not be empty"))

    assert response.status_code == 400
    assert response.json() == {
        "error": "bad_request",
        "code": 400,
        "message": "Trip name must not be empty",
    }


def test_trip_not_found_error_is_translated_to_404():
    response = login_with(TripNotFoundError("Trip not found"))

    assert response.status_code == 404
    assert response.json() == {"error": "not_found", "code": 404, "message": "Trip not found"}


def test_trip_access_denied_error_is_translated_to_403():
    response = login_with(TripAccessDeniedError("No access"))

    assert response.status_code == 403
    assert response.json() == {"error": "forbidden", "code": 403, "message": "No access"}


def test_invalid_destination_error_is_translated_to_400():
    response = login_with(InvalidDestinationError("Destination name must not be empty"))

    assert response.status_code == 400
    assert response.json() == {
        "error": "bad_request",
        "code": 400,
        "message": "Destination name must not be empty",
    }


def test_destination_not_found_error_is_translated_to_404():
    response = login_with(DestinationNotFoundError("Destination not found"))

    assert response.status_code == 404
    assert response.json() == {
        "error": "not_found",
        "code": 404,
        "message": "Destination not found",
    }


def test_invalid_activity_error_is_translated_to_400():
    response = login_with(InvalidActivityError("boom"))

    assert response.status_code == 400
    assert response.json() == {"error": "bad_request", "code": 400, "message": "boom"}


def test_activity_not_found_error_is_translated_to_404():
    response = login_with(ActivityNotFoundError("boom"))

    assert response.status_code == 404
    assert response.json() == {"error": "not_found", "code": 404, "message": "boom"}


def test_invalid_scheduled_activity_error_is_translated_to_400():
    response = login_with(InvalidScheduledActivityError("boom"))

    assert response.status_code == 400
    assert response.json() == {"error": "bad_request", "code": 400, "message": "boom"}


def test_scheduled_activity_not_found_error_is_translated_to_404():
    response = login_with(ScheduledActivityNotFoundError("boom"))

    assert response.status_code == 404
    assert response.json() == {"error": "not_found", "code": 404, "message": "boom"}


def test_already_collaborator_error_is_translated_to_409():
    response = login_with(AlreadyCollaboratorError("boom"))

    assert response.status_code == 409
    assert response.json() == {"error": "conflict", "code": 409, "message": "boom"}


def test_collaborator_not_found_error_is_translated_to_404():
    response = login_with(CollaboratorNotFoundError("boom"))

    assert response.status_code == 404
    assert response.json() == {"error": "not_found", "code": 404, "message": "boom"}


def test_unmapped_domain_error_falls_back_to_400():
    response = login_with(DomainError("Something is wrong"))

    assert response.status_code == 400
    assert response.json() == {"error": "bad_request", "code": 400, "message": "Something is wrong"}
