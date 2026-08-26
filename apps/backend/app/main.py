from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.metadata import get_project_metadata
from app.routers.v1 import router as v1_router
from app.services.storage import get_storage_service

project_metadata = get_project_metadata()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await get_storage_service().ensure_bucket()
    yield


app = FastAPI(title=project_metadata["description"], version=project_metadata["version"], lifespan=lifespan)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
