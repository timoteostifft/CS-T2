from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from recomendacoes_api.adapters.database.postgres_place_repository import Base
from recomendacoes_api.adapters.database.session import engine
from recomendacoes_api.adapters.rest.controllers import router as places_router
from recomendacoes_api.adapters.rest.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Places & Activity Recommendations API", lifespan=lifespan)
app.include_router(places_router)
register_exception_handlers(app)
