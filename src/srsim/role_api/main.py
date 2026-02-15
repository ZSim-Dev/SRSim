from fastapi import FastAPI

from srsim.role_api.api.router import router as api_router
from srsim.role_api.core.exception_handlers import register_exception_handlers

app = FastAPI(title="SRSim Role API")
register_exception_handlers(app)
app.include_router(api_router)
