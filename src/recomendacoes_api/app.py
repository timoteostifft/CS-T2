from fastapi import FastAPI

from recomendacoes_api.adapters.rest.controllers import router as places_router

app = FastAPI(title="Places & Activity Recommendations API")
app.include_router(places_router)
