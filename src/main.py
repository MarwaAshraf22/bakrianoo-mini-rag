from dotenv import load_dotenv
from fastapi import FastAPI

from routes import core, data

load_dotenv()

app = FastAPI()
app.include_router(core.base_router)
app.include_router(data.data_router)
