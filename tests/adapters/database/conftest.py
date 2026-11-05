import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from recomendacoes_api.adapters.database.postgres_user_repository import (
    Base,
    UserModel,  # noqa: F401
)


@pytest.fixture
def session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)

    return sessionmaker(bind=engine)
