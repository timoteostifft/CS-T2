class DomainError(Exception):
    pass


class InvalidPlaceError(DomainError):
    pass


class InvalidStateError(DomainError):
    pass


class InvalidCityError(DomainError):
    pass
