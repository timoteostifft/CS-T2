from fastapi import FastAPI

from recomendacoes_api.adapters.rest.controllers import router as places_router
from recomendacoes_api.adapters.rest.exception_handlers import register_exception_handlers

app = FastAPI(title="Places & Activity Recommendations API")
app.include_router(places_router)
register_exception_handlers(app)
