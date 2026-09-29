class DomainError(Exception):
    pass


class InvalidPlaceError(DomainError):
    pass


class PlaceNotFoundError(DomainError):
    pass


class InvalidRankWeightsError(DomainError):
    pass
