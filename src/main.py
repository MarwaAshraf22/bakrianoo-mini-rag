from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from helpers.config import Settings, get_settings
from routes import core, data
from stores.llm.llm_provider_factory import LLMProviderFactory
from stores.vectordb.vectordb_provider_factory import VectorDBProviderFactory

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

    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(settings)
    app.generation_client = llm_provider_factory.create(
        provider=settings.GENERATION_BACKEND
    )
    app.embedding_client = llm_provider_factory.create(
        provider=settings.EMBEDDING_BACKEND
    )
    app.vectordb_client = vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )
    app.vectordb_client.connect()
    app.generation_model.set_generation_model(settings.GENERATION_MODEL_ID)
    app.embedding_model.set_embedding_model(
        settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_SIZE
    )
    try:
        yield
    finally:
        app.mongodb_client.close()
        app.vectordb_client.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(core.base_router)
app.include_router(data.data_router)
