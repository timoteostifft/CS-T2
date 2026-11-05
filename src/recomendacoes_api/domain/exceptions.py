class DomainError(Exception):
    pass


class InvalidUserError(DomainError):
    pass


class EmailAlreadyRegisteredError(DomainError):
    pass


class InvalidCredentialsError(DomainError):
    pass


class InvalidTokenError(DomainError):
    pass


class InvalidTripError(DomainError):
    pass


class TripNotFoundError(DomainError):
    pass


class TripAccessDeniedError(DomainError):
    pass
