from datetime import date, datetime
from uuid import UUID

from recomendacoes_api.domain.entities import (
    FIRST_POSITION,
    MIN_PASSWORD_LENGTH,
    Activity,
    ActivityCategory,
    ActivityStatus,
    CollaboratorDetails,
    CollaboratorRole,
    Destination,
    DestinationCategory,
    Review,
    ReviewDetails,
    ScheduledActivity,
    ScheduledActivityDetails,
    Trip,
    User,
)
from recomendacoes_api.domain.exceptions import (
    ActivityNotFoundError,
    DestinationNotFoundError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidDestinationError,
    InvalidTokenError,
    InvalidUserError,
    ScheduledActivityNotFoundError,
    TripAccessDeniedError,
    TripNotFoundError,
)
from recomendacoes_api.domain.pagination import DEFAULT_LIMIT, Page
from recomendacoes_api.ports.repositories import (
    ActivityRepository,
    DestinationRepository,
    ReviewRepository,
    ScheduledActivityRepository,
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


def _get_viewable_trip(trip_repository: TripRepository, trip_id: UUID, user_id: UUID) -> Trip:
    trip = trip_repository.find_by_id(trip_id)

    if trip is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    if not trip.can_view(user_id):
        raise TripAccessDeniedError(f"User has no access to trip {trip_id}")

    return trip


def _get_editable_trip(trip_repository: TripRepository, trip_id: UUID, user_id: UUID) -> Trip:
    trip = _get_viewable_trip(trip_repository, trip_id, user_id)

    if not trip.can_edit(user_id):
        raise TripAccessDeniedError(f"User cannot edit trip {trip_id}")

    return trip


def _get_owned_trip(trip_repository: TripRepository, trip_id: UUID, user_id: UUID) -> Trip:
    trip = _get_viewable_trip(trip_repository, trip_id, user_id)

    if not trip.is_owned_by(user_id):
        raise TripAccessDeniedError(f"Only the owner can manage trip {trip_id}")

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
        return _get_viewable_trip(self._trip_repository, trip_id, user_id)


class SetTripBudgetUseCase:
    def __init__(self, trip_repository: TripRepository) -> None:
        self._trip_repository = trip_repository

    def execute(self, user_id: UUID, trip_id: UUID, amount: float) -> Trip:
        trip = _get_editable_trip(self._trip_repository, trip_id, user_id)

        trip.set_budget(amount)

        self._trip_repository.update(trip)

        return trip


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
        _get_editable_trip(self._trip_repository, trip_id, user_id)

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
        _get_viewable_trip(self._trip_repository, trip_id, user_id)

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
        _get_editable_trip(self._trip_repository, trip_id, user_id)

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
        _get_editable_trip(self._trip_repository, trip_id, user_id)
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
        _get_editable_trip(self._trip_repository, trip_id, user_id)

        current = self._destination_repository.list_by_trip(trip_id)
        by_id = {destination.id: destination for destination in current}

        if len(destination_ids) != len(set(destination_ids)) or set(destination_ids) != set(by_id):
            raise InvalidDestinationError(
                "Destination order must list every destination of the trip exactly once"
            )

        _renumber(self._destination_repository, [by_id[item] for item in destination_ids])


def _get_scheduled_activity(
    scheduled_repository: ScheduledActivityRepository,
    destination_id: UUID,
    scheduled_id: UUID,
) -> ScheduledActivity:
    scheduled = scheduled_repository.find_by_id(scheduled_id)

    if scheduled is None or scheduled.destination_id != destination_id:
        raise ScheduledActivityNotFoundError(f"Scheduled activity {scheduled_id} not found")

    return scheduled


def _with_activities(
    activity_repository: ActivityRepository, scheduled_items: list[ScheduledActivity]
) -> list[ScheduledActivityDetails]:
    activities = activity_repository.list_by_ids([item.activity_id for item in scheduled_items])
    by_id = {activity.id: activity for activity in activities}

    return [ScheduledActivityDetails(item, by_id[item.activity_id]) for item in scheduled_items]


class CreateActivityUseCase:
    def __init__(self, activity_repository: ActivityRepository) -> None:
        self._activity_repository = activity_repository

    def execute(
        self,
        name: str,
        category: ActivityCategory,
        location: str,
        description: str = "",
        photo_url: str | None = None,
    ) -> Activity:
        activity = Activity.create(name, category, location, description, photo_url)

        self._activity_repository.save(activity)

        return activity


class ListActivitiesUseCase:
    def __init__(self, activity_repository: ActivityRepository) -> None:
        self._activity_repository = activity_repository

    def execute(self, limit: int = DEFAULT_LIMIT, offset: int = 0) -> Page[Activity]:
        return Page(
            items=self._activity_repository.list_all(limit, offset),
            total=self._activity_repository.count_all(),
        )


class GetActivityUseCase:
    def __init__(self, activity_repository: ActivityRepository) -> None:
        self._activity_repository = activity_repository

    def execute(self, activity_id: UUID) -> Activity:
        activity = self._activity_repository.find_by_id(activity_id)

        if activity is None:
            raise ActivityNotFoundError(f"Activity {activity_id} not found")

        return activity


class ScheduleActivityUseCase:
    def __init__(
        self,
        trip_repository: TripRepository,
        destination_repository: DestinationRepository,
        activity_repository: ActivityRepository,
        scheduled_repository: ScheduledActivityRepository,
    ) -> None:
        self._trip_repository = trip_repository
        self._destination_repository = destination_repository
        self._activity_repository = activity_repository
        self._scheduled_repository = scheduled_repository

    def execute(
        self,
        user_id: UUID,
        trip_id: UUID,
        destination_id: UUID,
        activity_id: UUID,
        starts_at: datetime | None = None,
        duration_minutes: int | None = None,
        planned_cost: float = 0.0,
        status: ActivityStatus = ActivityStatus.PENDING,
    ) -> ScheduledActivityDetails:
        _get_editable_trip(self._trip_repository, trip_id, user_id)
        _get_destination(self._destination_repository, trip_id, destination_id)

        activity = self._activity_repository.find_by_id(activity_id)

        if activity is None:
            raise ActivityNotFoundError(f"Activity {activity_id} not found")

        scheduled = ScheduledActivity(
            destination_id=destination_id,
            activity_id=activity_id,
            starts_at=starts_at,
            duration_minutes=duration_minutes,
            planned_cost=planned_cost,
            status=status,
        )

        self._scheduled_repository.save(scheduled)

        return ScheduledActivityDetails(scheduled, activity)


class ListScheduledActivitiesUseCase:
    def __init__(
        self,
        trip_repository: TripRepository,
        destination_repository: DestinationRepository,
        activity_repository: ActivityRepository,
        scheduled_repository: ScheduledActivityRepository,
    ) -> None:
        self._trip_repository = trip_repository
        self._destination_repository = destination_repository
        self._activity_repository = activity_repository
        self._scheduled_repository = scheduled_repository

    def execute(
        self,
        user_id: UUID,
        trip_id: UUID,
        destination_id: UUID,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> Page[ScheduledActivityDetails]:
        _get_viewable_trip(self._trip_repository, trip_id, user_id)
        _get_destination(self._destination_repository, trip_id, destination_id)

        scheduled_items = self._scheduled_repository.list_by_destination(
            destination_id, limit, offset
        )

        return Page(
            items=_with_activities(self._activity_repository, scheduled_items),
            total=self._scheduled_repository.count_by_destination(destination_id),
        )


class UpdateScheduledActivityUseCase:
    def __init__(
        self,
        trip_repository: TripRepository,
        destination_repository: DestinationRepository,
        activity_repository: ActivityRepository,
        scheduled_repository: ScheduledActivityRepository,
    ) -> None:
        self._trip_repository = trip_repository
        self._destination_repository = destination_repository
        self._activity_repository = activity_repository
        self._scheduled_repository = scheduled_repository

    def execute(
        self,
        user_id: UUID,
        trip_id: UUID,
        destination_id: UUID,
        scheduled_id: UUID,
        starts_at: datetime | None,
        duration_minutes: int | None,
        planned_cost: float,
        status: ActivityStatus,
    ) -> ScheduledActivityDetails:
        _get_editable_trip(self._trip_repository, trip_id, user_id)
        _get_destination(self._destination_repository, trip_id, destination_id)

        scheduled = _get_scheduled_activity(
            self._scheduled_repository, destination_id, scheduled_id
        )

        scheduled.update(starts_at, duration_minutes, planned_cost, status)

        self._scheduled_repository.update(scheduled)

        return _with_activities(self._activity_repository, [scheduled])[0]


class RemoveScheduledActivityUseCase:
    def __init__(
        self,
        trip_repository: TripRepository,
        destination_repository: DestinationRepository,
        scheduled_repository: ScheduledActivityRepository,
    ) -> None:
        self._trip_repository = trip_repository
        self._destination_repository = destination_repository
        self._scheduled_repository = scheduled_repository

    def execute(
        self, user_id: UUID, trip_id: UUID, destination_id: UUID, scheduled_id: UUID
    ) -> None:
        _get_editable_trip(self._trip_repository, trip_id, user_id)
        _get_destination(self._destination_repository, trip_id, destination_id)
        _get_scheduled_activity(self._scheduled_repository, destination_id, scheduled_id)

        self._scheduled_repository.delete(scheduled_id)


class JoinTripUseCase:
    def __init__(self, trip_repository: TripRepository) -> None:
        self._trip_repository = trip_repository

    def execute(self, user_id: UUID, invite_code: str) -> Trip:
        trip = self._trip_repository.find_by_invite_code(invite_code.strip().upper())

        if trip is None:
            raise TripNotFoundError("No trip matches this invite code")

        trip.add_collaborator(user_id)

        self._trip_repository.update(trip)

        return trip


class ListCollaboratorsUseCase:
    def __init__(self, trip_repository: TripRepository, user_repository: UserRepository) -> None:
        self._trip_repository = trip_repository
        self._user_repository = user_repository

    def execute(
        self, user_id: UUID, trip_id: UUID, limit: int = DEFAULT_LIMIT, offset: int = 0
    ) -> Page[CollaboratorDetails]:
        trip = _get_viewable_trip(self._trip_repository, trip_id, user_id)

        selected = trip.collaborators[offset : offset + limit]
        users = self._user_repository.list_by_ids([item.user_id for item in selected])
        by_id = {user.id: user for user in users}

        return Page(
            items=[CollaboratorDetails(item, by_id[item.user_id]) for item in selected],
            total=len(trip.collaborators),
        )


class ChangeCollaboratorRoleUseCase:
    def __init__(self, trip_repository: TripRepository, user_repository: UserRepository) -> None:
        self._trip_repository = trip_repository
        self._user_repository = user_repository

    def execute(
        self, user_id: UUID, trip_id: UUID, collaborator_user_id: UUID, role: CollaboratorRole
    ) -> CollaboratorDetails:
        trip = _get_owned_trip(self._trip_repository, trip_id, user_id)

        collaborator = trip.change_collaborator_role(collaborator_user_id, role)

        self._trip_repository.update(trip)

        user = self._user_repository.list_by_ids([collaborator_user_id])[0]

        return CollaboratorDetails(collaborator, user)


class RemoveCollaboratorUseCase:
    def __init__(self, trip_repository: TripRepository) -> None:
        self._trip_repository = trip_repository

    def execute(self, user_id: UUID, trip_id: UUID, collaborator_user_id: UUID) -> None:
        trip = _get_owned_trip(self._trip_repository, trip_id, user_id)

        trip.remove_collaborator(collaborator_user_id)

        self._trip_repository.update(trip)


class SubmitReviewUseCase:
    def __init__(
        self, activity_repository: ActivityRepository, review_repository: ReviewRepository
    ) -> None:
        self._activity_repository = activity_repository
        self._review_repository = review_repository

    def execute(
        self, user: User, activity_id: UUID, rating: int, comment: str | None = None
    ) -> ReviewDetails:
        review = Review.create(activity_id, user.id, rating, comment)
        activity = self._activity_repository.find_by_id(activity_id)

        if activity is None:
            raise ActivityNotFoundError(f"Activity {activity_id} not found")

        existing = self._review_repository.find_by_activity_and_user(activity_id, user.id)

        if existing is None:
            self._review_repository.save(review)
        else:
            existing.update(rating, comment)
            self._review_repository.update(existing)
            review = existing

        activity.recalculate_rating(self._review_repository.list_ratings_by_activity(activity_id))

        self._activity_repository.update(activity)

        return ReviewDetails(review, user)


class ListReviewsUseCase:
    def __init__(
        self,
        activity_repository: ActivityRepository,
        review_repository: ReviewRepository,
        user_repository: UserRepository,
    ) -> None:
        self._activity_repository = activity_repository
        self._review_repository = review_repository
        self._user_repository = user_repository

    def execute(
        self, activity_id: UUID, limit: int = DEFAULT_LIMIT, offset: int = 0
    ) -> Page[ReviewDetails]:
        if self._activity_repository.find_by_id(activity_id) is None:
            raise ActivityNotFoundError(f"Activity {activity_id} not found")

        reviews = self._review_repository.list_by_activity(activity_id, limit, offset)
        users = self._user_repository.list_by_ids([review.user_id for review in reviews])
        by_id = {user.id: user for user in users}

        return Page(
            items=[ReviewDetails(review, by_id[review.user_id]) for review in reviews],
            total=self._review_repository.count_by_activity(activity_id),
        )
