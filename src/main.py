from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from helpers.config import Settings, get_settings
from routes import core, data

load_dotenv()


# @app.on_event("startup")
# async def startup_db_client():
#     settings: Settings = get_settings()
#     app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URI)
#     app.database = app.mongodb_client[settings.MONGODB_DATABASE]

# @app.on_event("shutdown")
# async def shutdown_db_client():
#     app.mongodb_client.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = get_settings()
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URI)
    app.database = app.mongodb_client[settings.MONGODB_DATABASE]
    try:
        yield
    finally:
        app.mongodb_client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(core.base_router)
app.include_router(data.data_router)
