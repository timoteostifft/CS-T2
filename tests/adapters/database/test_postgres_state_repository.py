from recomendacoes_api.adapters.database.postgres_state_repository import (
    PostgresStateRepository,
    StateModel,
)


def test_list_all_returns_states_ordered_by_name(session_factory):
    with session_factory() as session:
        session.add_all(
            [
                StateModel(code="SC", name="Santa Catarina"),
                StateModel(code="AC", name="Acre"),
            ]
        )
        session.commit()

    states = PostgresStateRepository(session_factory).list_all()

    assert [(state.code, state.name) for state in states] == [
        ("AC", "Acre"),
        ("SC", "Santa Catarina"),
    ]


def seed(session_factory) -> PostgresStateRepository:
    with session_factory() as session:
        session.add_all(
            [
                StateModel(code="SC", name="Santa Catarina"),
                StateModel(code="AC", name="Acre"),
                StateModel(code="RS", name="Rio Grande do Sul"),
            ]
        )
        session.commit()

    return PostgresStateRepository(session_factory)


def test_list_all_applies_limit_and_offset(session_factory):
    repository = seed(session_factory)

    states = repository.list_all(limit=1, offset=1)

    assert [state.code for state in states] == ["RS"]


def test_count_all_returns_the_number_of_states(session_factory):
    assert seed(session_factory).count_all() == 3
