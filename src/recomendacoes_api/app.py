from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from recomendacoes_api.adapters.database.location_seed import seed_locations
from recomendacoes_api.adapters.database.postgres_place_repository import Base
from recomendacoes_api.adapters.database.session import engine, sessions
from recomendacoes_api.adapters.rest.controllers import cities_router, states_router
from recomendacoes_api.adapters.rest.controllers import router as places_router
from recomendacoes_api.adapters.rest.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    Base.metadata.create_all(bind=engine)
    seed_locations(sessions)
    yield


app = FastAPI(title="Places & Activity Recommendations API", lifespan=lifespan)
app.include_router(places_router)
app.include_router(states_router)
app.include_router(cities_router)
register_exception_handlers(app)
