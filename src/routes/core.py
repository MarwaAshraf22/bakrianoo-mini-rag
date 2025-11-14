from fastapi import APIRouter, Depends

from helpers.config import Settings, get_settings

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)


@base_router.get("/healthcheck")
async def healthcheck(app_settings: Settings = Depends(get_settings)):
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    return {
        "status": "ok",
        "app_name": app_name,
        "app_version": app_version,
    }
