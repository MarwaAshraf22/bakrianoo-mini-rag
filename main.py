from dotenv import load_dotenv
from fastapi import FastAPI

from routes import core

load_dotenv()

app = FastAPI()
app.include_router(core.base_router)
