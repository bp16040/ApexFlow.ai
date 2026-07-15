from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.routes.health import router as health_router

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(settings.log_level)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.include_router(health_router)
