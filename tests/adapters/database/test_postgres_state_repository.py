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
