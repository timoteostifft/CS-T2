class DomainError(Exception):
    pass


class InvalidPlaceError(DomainError):
    pass


class PlaceNotFoundError(DomainError):
    pass


class InvalidStateError(DomainError):
    pass


class InvalidCityError(DomainError):
    pass
