from recomendacoes_api.adapters.rest import dependencies
from recomendacoes_api.application.use_cases import (
    AddDestinationUseCase,
    ChangeCollaboratorRoleUseCase,
    CreateActivityUseCase,
    CreateTripUseCase,
    DeleteDestinationUseCase,
    DeleteTripUseCase,
    GetActivityUseCase,
    GetCurrentUserUseCase,
    GetTripUseCase,
    JoinTripUseCase,
    ListActivitiesUseCase,
    ListCollaboratorsUseCase,
    ListDestinationsUseCase,
    ListReviewsUseCase,
    ListScheduledActivitiesUseCase,
    ListTripsUseCase,
    LoginUserUseCase,
    RegisterUserUseCase,
    RemoveCollaboratorUseCase,
    RemoveScheduledActivityUseCase,
    ReorderDestinationsUseCase,
    ScheduleActivityUseCase,
    SetTripBudgetUseCase,
    SubmitReviewUseCase,
    UpdateDestinationUseCase,
    UpdateScheduledActivityUseCase,
    UpdateTripUseCase,
)


def test_collaborators_are_cached_singletons():
    assert dependencies.get_user_repository() is dependencies.get_user_repository()
    assert dependencies.get_trip_repository() is dependencies.get_trip_repository()
    assert dependencies.get_destination_repository() is dependencies.get_destination_repository()
    assert dependencies.get_activity_repository() is dependencies.get_activity_repository()
    assert (
        dependencies.get_scheduled_activity_repository()
        is dependencies.get_scheduled_activity_repository()
    )
    assert dependencies.get_review_repository() is dependencies.get_review_repository()
    assert dependencies.get_password_hasher() is dependencies.get_password_hasher()
    assert dependencies.get_token_service() is dependencies.get_token_service()


def test_use_case_providers_build_the_expected_use_cases():
    assert isinstance(dependencies.get_register_user_use_case(), RegisterUserUseCase)
    assert isinstance(dependencies.get_login_user_use_case(), LoginUserUseCase)
    assert isinstance(dependencies.get_get_current_user_use_case(), GetCurrentUserUseCase)
    assert isinstance(dependencies.get_create_trip_use_case(), CreateTripUseCase)
    assert isinstance(dependencies.get_list_trips_use_case(), ListTripsUseCase)
    assert isinstance(dependencies.get_get_trip_use_case(), GetTripUseCase)
    assert isinstance(dependencies.get_update_trip_use_case(), UpdateTripUseCase)
    assert isinstance(dependencies.get_delete_trip_use_case(), DeleteTripUseCase)
    assert isinstance(dependencies.get_add_destination_use_case(), AddDestinationUseCase)
    assert isinstance(dependencies.get_list_destinations_use_case(), ListDestinationsUseCase)
    assert isinstance(dependencies.get_update_destination_use_case(), UpdateDestinationUseCase)
    assert isinstance(dependencies.get_delete_destination_use_case(), DeleteDestinationUseCase)
    assert isinstance(dependencies.get_reorder_destinations_use_case(), ReorderDestinationsUseCase)
    assert isinstance(dependencies.get_create_activity_use_case(), CreateActivityUseCase)
    assert isinstance(dependencies.get_list_activities_use_case(), ListActivitiesUseCase)
    assert isinstance(dependencies.get_get_activity_use_case(), GetActivityUseCase)
    assert isinstance(dependencies.get_schedule_activity_use_case(), ScheduleActivityUseCase)
    assert isinstance(
        dependencies.get_list_scheduled_activities_use_case(), ListScheduledActivitiesUseCase
    )
    assert isinstance(
        dependencies.get_update_scheduled_activity_use_case(), UpdateScheduledActivityUseCase
    )
    assert isinstance(
        dependencies.get_remove_scheduled_activity_use_case(), RemoveScheduledActivityUseCase
    )
    assert isinstance(dependencies.get_set_trip_budget_use_case(), SetTripBudgetUseCase)
    assert isinstance(dependencies.get_join_trip_use_case(), JoinTripUseCase)
    assert isinstance(dependencies.get_list_collaborators_use_case(), ListCollaboratorsUseCase)
    assert isinstance(
        dependencies.get_change_collaborator_role_use_case(), ChangeCollaboratorRoleUseCase
    )
    assert isinstance(dependencies.get_remove_collaborator_use_case(), RemoveCollaboratorUseCase)
    assert isinstance(dependencies.get_submit_review_use_case(), SubmitReviewUseCase)
    assert isinstance(dependencies.get_list_reviews_use_case(), ListReviewsUseCase)
