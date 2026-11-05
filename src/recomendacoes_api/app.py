from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from recomendacoes_api.adapters.database.postgres_user_repository import Base
from recomendacoes_api.adapters.database.session import engine
from recomendacoes_api.adapters.rest.controllers import auth_router, health_router, trips_router
from recomendacoes_api.adapters.rest.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="ViajaJunto API", lifespan=lifespan)
API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(trips_router, prefix=API_PREFIX)
app.include_router(health_router, prefix=API_PREFIX)

register_exception_handlers(app)
