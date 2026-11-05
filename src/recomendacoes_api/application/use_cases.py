from datetime import date
from uuid import UUID

from recomendacoes_api.domain.entities import (
    FIRST_POSITION,
    MIN_PASSWORD_LENGTH,
    Destination,
    DestinationCategory,
    Trip,
    User,
)
from recomendacoes_api.domain.exceptions import (
    DestinationNotFoundError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidDestinationError,
    InvalidTokenError,
    InvalidUserError,
    TripAccessDeniedError,
    TripNotFoundError,
)
from recomendacoes_api.domain.pagination import DEFAULT_LIMIT, Page
from recomendacoes_api.ports.repositories import (
    DestinationRepository,
    TripRepository,
    UserRepository,
)
from recomendacoes_api.ports.security import PasswordHasher, TokenService


class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    def execute(self, name: str, email: str, password: str) -> User:
        if len(password) < MIN_PASSWORD_LENGTH:
            raise InvalidUserError(f"Password must have at least {MIN_PASSWORD_LENGTH} characters")

        user = User.create(
            name=name, email=email, password_hash=self._password_hasher.hash(password)
        )

        if self._user_repository.find_by_email(user.email) is not None:
            raise EmailAlreadyRegisteredError(f"Email {user.email} is already registered")

        self._user_repository.save(user)

        return user


class LoginUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_service = token_service

    def execute(self, email: str, password: str) -> str:
        user = self._user_repository.find_by_email(User.normalize_email(email))

        if user is None or not self._password_hasher.verify(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        return self._token_service.issue(user.id)


class GetCurrentUserUseCase:
    def __init__(self, user_repository: UserRepository, token_service: TokenService) -> None:
        self._user_repository = user_repository
        self._token_service = token_service

    def execute(self, token: str | None) -> User:
        if token is None:
            raise InvalidTokenError("Authentication token is missing")

        user = self._user_repository.find_by_id(self._token_service.read_subject(token))

        if user is None:
            raise InvalidTokenError("Authentication token does not match any user")

        return user


def _get_owned_trip(trip_repository: TripRepository, trip_id: UUID, user_id: UUID) -> Trip:
    trip = trip_repository.find_by_id(trip_id)

    if trip is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    if not trip.is_owned_by(user_id):
        raise TripAccessDeniedError(f"User has no access to trip {trip_id}")

    return trip


class CreateTripUseCase:
    def __init__(self, trip_repository: TripRepository) -> None:
        self._trip_repository = trip_repository

    def execute(
        self, user_id: UUID, name: str, description: str, start_date: date, end_date: date
    ) -> Trip:
        trip = Trip.create(name, description, start_date, end_date, owner_id=user_id)

        self._trip_repository.save(trip)

        return trip


class ListTripsUseCase:
    def __init__(self, trip_repository: TripRepository) -> None:
        self._trip_repository = trip_repository

    def execute(self, user_id: UUID, limit: int = DEFAULT_LIMIT, offset: int = 0) -> Page[Trip]:
        return Page(
            items=self._trip_repository.list_by_user(user_id, limit, offset),
            total=self._trip_repository.count_by_user(user_id),
        )


class GetTripUseCase:
    def __init__(self, trip_repository: TripRepository) -> None:
        self._trip_repository = trip_repository

    def execute(self, user_id: UUID, trip_id: UUID) -> Trip:
        return _get_owned_trip(self._trip_repository, trip_id, user_id)


class UpdateTripUseCase:
    def __init__(self, trip_repository: TripRepository) -> None:
        self._trip_repository = trip_repository

    def execute(
        self,
        user_id: UUID,
        trip_id: UUID,
        name: str,
        description: str,
        start_date: date,
        end_date: date,
    ) -> Trip:
        trip = _get_owned_trip(self._trip_repository, trip_id, user_id)

        trip.update(name, description, start_date, end_date)

        self._trip_repository.update(trip)

        return trip


class DeleteTripUseCase:
    def __init__(self, trip_repository: TripRepository) -> None:
        self._trip_repository = trip_repository

    def execute(self, user_id: UUID, trip_id: UUID) -> None:
        _get_owned_trip(self._trip_repository, trip_id, user_id)

        self._trip_repository.delete(trip_id)


def _get_destination(
    destination_repository: DestinationRepository, trip_id: UUID, destination_id: UUID
) -> Destination:
    destination = destination_repository.find_by_id(destination_id)

    if destination is None or destination.trip_id != trip_id:
        raise DestinationNotFoundError(f"Destination {destination_id} not found")

    return destination


def _renumber(destination_repository: DestinationRepository, destinations: list[Destination]):
    for index, destination in enumerate(destinations, start=FIRST_POSITION):
        destination.move_to(index)

    destination_repository.update_many(destinations)


class AddDestinationUseCase:
    def __init__(
        self, trip_repository: TripRepository, destination_repository: DestinationRepository
    ) -> None:
        self._trip_repository = trip_repository
        self._destination_repository = destination_repository

    def execute(
        self,
        user_id: UUID,
        trip_id: UUID,
        name: str,
        location: str,
        category: DestinationCategory,
        arrival_date: date,
        departure_date: date,
        photo_url: str | None = None,
        description: str = "",
    ) -> Destination:
        _get_owned_trip(self._trip_repository, trip_id, user_id)

        destination = Destination.create(
            trip_id=trip_id,
            name=name,
            location=location,
            category=category,
            arrival_date=arrival_date,
            departure_date=departure_date,
            position=self._destination_repository.count_by_trip(trip_id) + FIRST_POSITION,
            photo_url=photo_url,
            description=description,
        )

        self._destination_repository.save(destination)

        return destination


class ListDestinationsUseCase:
    def __init__(
        self, trip_repository: TripRepository, destination_repository: DestinationRepository
    ) -> None:
        self._trip_repository = trip_repository
        self._destination_repository = destination_repository

    def execute(
        self, user_id: UUID, trip_id: UUID, limit: int = DEFAULT_LIMIT, offset: int = 0
    ) -> Page[Destination]:
        _get_owned_trip(self._trip_repository, trip_id, user_id)

        return Page(
            items=self._destination_repository.list_by_trip(trip_id, limit, offset),
            total=self._destination_repository.count_by_trip(trip_id),
        )


class UpdateDestinationUseCase:
    def __init__(
        self, trip_repository: TripRepository, destination_repository: DestinationRepository
    ) -> None:
        self._trip_repository = trip_repository
        self._destination_repository = destination_repository

    def execute(
        self,
        user_id: UUID,
        trip_id: UUID,
        destination_id: UUID,
        name: str,
        location: str,
        category: DestinationCategory,
        arrival_date: date,
        departure_date: date,
        photo_url: str | None = None,
        description: str = "",
    ) -> Destination:
        _get_owned_trip(self._trip_repository, trip_id, user_id)

        destination = _get_destination(self._destination_repository, trip_id, destination_id)

        destination.update(
            name, location, category, arrival_date, departure_date, photo_url, description
        )

        self._destination_repository.update(destination)

        return destination


class DeleteDestinationUseCase:
    def __init__(
        self, trip_repository: TripRepository, destination_repository: DestinationRepository
    ) -> None:
        self._trip_repository = trip_repository
        self._destination_repository = destination_repository

    def execute(self, user_id: UUID, trip_id: UUID, destination_id: UUID) -> None:
        _get_owned_trip(self._trip_repository, trip_id, user_id)
        _get_destination(self._destination_repository, trip_id, destination_id)

        self._destination_repository.delete(destination_id)

        remaining = self._destination_repository.list_by_trip(trip_id)

        _renumber(self._destination_repository, remaining)


class ReorderDestinationsUseCase:
    def __init__(
        self, trip_repository: TripRepository, destination_repository: DestinationRepository
    ) -> None:
        self._trip_repository = trip_repository
        self._destination_repository = destination_repository

    def execute(self, user_id: UUID, trip_id: UUID, destination_ids: list[UUID]) -> None:
        _get_owned_trip(self._trip_repository, trip_id, user_id)

        current = self._destination_repository.list_by_trip(trip_id)
        by_id = {destination.id: destination for destination in current}

        if len(destination_ids) != len(set(destination_ids)) or set(destination_ids) != set(by_id):
            raise InvalidDestinationError(
                "Destination order must list every destination of the trip exactly once"
            )

        _renumber(self._destination_repository, [by_id[item] for item in destination_ids])
