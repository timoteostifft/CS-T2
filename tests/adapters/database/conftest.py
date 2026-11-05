import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from recomendacoes_api.adapters.database.postgres_city_repository import CityModel  # noqa: F401
from recomendacoes_api.adapters.database.postgres_place_repository import Base
from recomendacoes_api.adapters.database.postgres_report_repository import ReportModel  # noqa: F401
from recomendacoes_api.adapters.database.postgres_review_repository import ReviewModel  # noqa: F401
from recomendacoes_api.adapters.database.postgres_state_repository import StateModel  # noqa: F401


@pytest.fixture
def session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)

    return sessionmaker(bind=engine)
