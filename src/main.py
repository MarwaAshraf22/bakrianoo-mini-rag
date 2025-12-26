from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from helpers.config import Settings, get_settings
from routes import core, data, nlp
from stores.llm.llm_provider_factory import LLMProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from stores.vectordb.vectordb_provider_factory import VectorDBProviderFactory

# from motor.motor_asyncio import AsyncIOMotorClient

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
    # app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URI)
    # app.database = app.mongodb_client[settings.MONGODB_DATABASE]

    postgres_uri = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_ROOT_DB}"
    app.db_engine = create_async_engine(postgres_uri)
    app.database = sessionmaker(
        app.db_engine, class_=AsyncSession, expire_on_commit=False
    )

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
    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANGUAGE, default_language=settings.DEFAULT_LANGUAGE
    )

    app.vectordb_client.connect()
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)
    app.embedding_client.set_embedding_model(
        settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_MODEL_SIZE
    )
    try:
        yield
    finally:
        # app.mongodb_client.close()
        app.vectordb_client.disconnect()
        app.db_engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(core.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
