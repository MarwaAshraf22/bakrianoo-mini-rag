import os

from fastapi import APIRouter

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)


@base_router.get("/healthcheck")
async def healthcheck():
    app_name = os.getenv("APP_NAME", "unknown")
    app_version = os.getenv("APP_VERSION", "unknown")
    return {
        "status": "ok",
        "app_name": app_name,
        "app_version": app_version,
    }
