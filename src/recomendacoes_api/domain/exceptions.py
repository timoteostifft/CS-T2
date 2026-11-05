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


class InvalidDestinationError(DomainError):
    pass


class DestinationNotFoundError(DomainError):
    pass


class InvalidActivityError(DomainError):
    pass


class ActivityNotFoundError(DomainError):
    pass


class InvalidScheduledActivityError(DomainError):
    pass


class ScheduledActivityNotFoundError(DomainError):
    pass


class AlreadyCollaboratorError(DomainError):
    pass


class CollaboratorNotFoundError(DomainError):
    pass


class InvalidReviewError(DomainError):
    pass
